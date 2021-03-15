import argparse
import time

import lxml.html
import requests


def parser(argv):
    p = argparse.ArgumentParser()
    p.add_argument('gitlab_url', help='url to the gitlab instance (e.g. http://gitlab:80)')
    p.add_argument('--admin-password', help='password to assign or use for the admin user')
    return p.parse_args(argv)


def parse_form(session, url, form_id):
    """Returns the form fields and action

    We get the form fields because there are server generated values
    that need to be carried across to the form post

    """
    resp = session.get(url)
    html = lxml.html.document_fromstring(resp.content)
    try:
        form = html.get_element_by_id(form_id)
    except KeyError:  # NoneType
        raise RuntimeError(f'form not found in {resp} for {url}')
    return dict(form.fields), form.action


def main(argv=None):
    args = parser(argv)
    gitlab_url = args.gitlab_url
    admin_password = args.admin_password

    sign_in_url = f'{gitlab_url}/users/sign_in'

    session = requests.Session()

    # Go directly to the sign in...
    # On installation this will redirect the user to a form to assign the 'root'/admin user password.
    # If the installation is already complete we'll land on the signin form.
    retry_count = 0
    while True:
        resp = session.get(sign_in_url, allow_redirects=False)
        try:
            assert resp.status_code < 500, resp
        except AssertionError:
            # the gitlab service isn't up quite yet
            if retry_count >= 4:
                print("Something unexpected happen during the setup of GitLab")
                raise
            retry_count += 1
            time.sleep(30)
        else:
            break

    if resp.status_code == 302:  # assume new installation; assign password
        form_data, action = parse_form(session, sign_in_url, 'new_user')
        url = f'{gitlab_url}{action}'
        form_data['user[password]'] = admin_password
        form_data['user[password_comfirmation]'] = admin_password
        resp = session.post(url, data=form_data)
        assert resp.status_code == 200, resp

    # Sign In
    form_data, action = parse_form(session, sign_in_url, 'new_user')
    url = f'{gitlab_url}{action}'
    form_data['user[login]'] = 'root'
    form_data['user[password]'] = admin_password
    resp = session.post(url, data=form_data)
    assert resp.status_code == 200, resp

    # Create a Personal Access Token
    url = f'{gitlab_url}/-/profile/personal_access_tokens'
    form_data, action = parse_form(session, url, 'new_personal_access_token')
    url = f'{gitlab_url}{action}'
    form_data['personal_access_token[name]'] = 'gitlab cli'
    form_data['personal_access_token[scopes][]'] = 'api'
    resp = session.post(url, data=form_data)
    assert resp.status_code == 200, resp
    # Pull the PAT out of the page
    html = lxml.html.document_fromstring(resp.content)
    personal_access_token = html.get_element_by_id('created-personal-access-token').value
    print(personal_access_token)


if __name__ == '__main__':
    main()