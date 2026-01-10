import argparse
import pathlib
import re
import sys
import tempfile

import bioblend.toolshed
import git
import yaml

ts = bioblend.toolshed.ToolShedInstance(url='https://toolshed.g2.bx.psu.edu')
default_repo_url = 'https://github.com/BMCV/galaxy-image-analysis.git'


def list_tool_suite_dependencies(repo_name, repo_owner):
    install_info = ts.repositories.get_repository_revision_install_info(
        repo_name,
        repo_owner,
        list_revisions(repo_name, repo_owner)[-1],
    )
    suite_structure = install_info[2][repo_name][5]
    for repo_info in suite_structure[
        suite_structure['root_key']
    ]:
        yield repo_info[1], repo_owner


def list_tool_repositories(repo_url: str):
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = pathlib.Path(tempdir_str)
        git.Repo.clone_from(repo_url, tempdir_str)
        for shed_yml_path in tempdir.glob(
            'tools/**/.shed.y*ml',
            case_sensitive=False,
        ):
            if re.match(r'^.*\.ya?ml$', str(shed_yml_path).lower()):
                with shed_yml_path.open('r') as fp:
                    shed = yaml.safe_load(fp)
                repo_name = (
                    shed.get('suite', dict()).get('name')
                    or shed.get('name')
                )
                repo_owner = shed.get('owner')
                if repo_name and repo_owner:
                    if repo_name.startswith('suite_'):
                        yield from list_tool_suite_dependencies(
                            repo_name,
                            repo_owner,
                        )
                    else:
                        yield repo_name, repo_owner


def list_revisions(repo_name: str, repo_owner: str) -> list[str]:
    try:
        return ts.repositories.get_ordered_installable_revisions(
            repo_name,
            repo_owner,
        )
    except Exception as e:
        print(e, file=sys.stderr)
        return list()


class SectionIndex:

    def __init__(self, default='Miscellaneous'):
        with open('sections.yml', 'r') as fp:
            sections = yaml.safe_load(fp)['sections']
        self._default = default
        self._data = dict()
        self._used = set()
        for section in sections:
            for tool in section.get('tools', list()):
                if tool in self._data:
                    raise ValueError(
                        f'Tool "{tool}" defined in multple sections.',
                    )
                self._data[tool] = section

    def __getitem__(self, repo_name: str) -> str:
        if repo_name in self._data:
            self._used.add(repo_name)
            return self._data[repo_name]['name']
        else:
            return self._default

    @property
    def unused(self) -> list[str]:
        return list(sorted(frozenset(self._data.keys()) - self._used))


def build_tools_dict(repo_url: str, verbose: bool = False) -> dict:
    tools = list()
    sections = SectionIndex()
    for repo_name, repo_owner in list_tool_repositories(repo_url):
        tool_revisions = list_revisions(repo_name, repo_owner)
        if len(tool_revisions) > 0:
            tools.append(
                dict(
                    name=repo_name,
                    owner=repo_owner,
                    revisions=[tool_revisions[-1]],
                    tool_panel_section_label=sections[repo_name],
                ),
            )
            if verbose:
                print(
                    f'{tools[-1]["owner"]}/{tools[-1]["name"]}:',
                    f'{tools[-1]["revisions"]}',
                    f'({tools[-1]["tool_panel_section_label"]})'
                )
    if sections.unused:
        print(
            (
                'Tools defined in sections but not found:\n' +
                '\n'.join(f'- {tool}' for tool in sections.unused)
            ),
            file=sys.stderr,
        )
    tools.sort(key=lambda tool: tool['name'])
    return dict(
        tools=tools,
        install_resolver_dependencies=False,

        # Keep the image small, skip Conda dependencies, run the container
        # with `--priviledged` to employ Singularity constainers instead:
        install_tool_dependencies=False,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-url', type=str, default=default_repo_url)
    parser.add_argument('tools_file', type=str)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    tools_dict = build_tools_dict(args.repo_url, verbose=args.verbose)
    with open(args.tools_file, 'w') as fp:
        yaml.dump(tools_dict, fp)
