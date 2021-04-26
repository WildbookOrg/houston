# -*- coding: utf-8 -*-

from collections import namedtuple
import datetime
import json
from pathlib import Path

import git


class GitRemote:
    def __new__(self, remote_uri, **kwargs):
        if remote_uri.startswith('http'):
            import gitlab

            gl = gitlab.Gitlab(remote_uri, **kwargs)
            gl.GitRemoteDeleteError = gitlab.GitlabDeleteError
            return gl
        else:

            class GitRemoteDeleteError(Exception):
                pass

            gl = GitRemoteLocal(remote_uri, **kwargs)
            gl.GitRemoteDeleteError = GitRemoteDeleteError
            return gl


class GitRemoteLocal:
    def __init__(self, remote_uri, **kwargs):
        self.root = Path(remote_uri)
        self.root.mkdir(parents=True, exist_ok=True)
        self.namespaces = LocalNamespaces()
        self.groups = LocalGroups(self)
        self.projects = LocalProjects(self, self.root)
        self.user = LocalUser('user_id')

    def auth(self):
        # Not implementing auth
        pass


LocalUser = namedtuple('LocalUser', ['id'])
LocalNamespace = namedtuple('LocalNamespace', ['id', 'name'])


class LocalNamespaces:
    # Not implementing namespace

    def get(self, id):
        # namespace is always found
        return LocalNamespace(id, id)

    def list(self, search):
        # namespace is always found
        return [LocalNamespace(search, search)]


class LocalGroup:
    def __init__(self, id, git_remote):
        self.id = id
        # group projects is the same as the global projects
        self.projects = git_remote.projects


class LocalGroups:
    # Not implementing groups
    def __init__(self, git_remote):
        self.git_remote = git_remote

    def create(self, args):
        return LocalGroup(args['name'], self.git_remote)

    def get(self, id, **kwargs):
        return LocalGroup(id, self.git_remote)


LocalProject = namedtuple(
    'LocalProject',
    [
        'path',
        'description',
        'namespace',
        'tag_list',
        'web_url',
        'created_at',
        'id',
        'path_with_namespace',
    ],
)


class LocalProjects:
    def __init__(self, git_remote, root):
        self.git_remote = git_remote
        self.root = root
        self.projects_path = self.root / 'projects.json'
        self.projects = {}
        if self.projects_path.exists():
            with self.projects_path.open('r') as f:
                try:
                    projects = json.load(f)
                    for key, project in projects.items():
                        if (self.root / key).exists():
                            self.projects[key] = LocalProject(*project)
                except (json.decoder.JSONDecodeError, TypeError):
                    self.projects = {}

    def list(self, search, **kwargs):
        search = str(search)
        if search in self.projects:
            return [self.projects[search]]
        return []

    def create(self, args, **kwargs):
        project = LocalProject(
            path=args['path'],
            tag_list=sorted(args['tag_list']),
            description=args['description'],
            namespace={'id': args['namespace_id'], 'name': args['namespace_id']},
            web_url=str(self.root / args['path']),
            created_at=f'{datetime.datetime.now().isoformat()}Z',
            id=args['path'],
            path_with_namespace=f"{args['path']} {args['namespace_id']}",
        )
        git.Repo.init(project.web_url, bare=True)
        self.projects[project.path] = project
        with self.projects_path.open('w') as f:
            json.dump(self.projects, f)
        return project

    def delete(self, id):
        if id in self.projects:
            self.projects.pop(id)
            with self.projects_path.open('w') as f:
                json.dump(self.projects, f)
        else:
            raise self.git_remote.GitRemoteDeleteError()