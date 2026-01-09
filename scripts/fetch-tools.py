import argparse
import pathlib
import re
import sys
import tempfile

import bioblend.toolshed
import git
import yaml

ts = bioblend.toolshed.ToolShedInstance(url='https://toolshed.g2.bx.psu.edu')


def list_tool_repositories(repo_url: str):
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = pathlib.Path(tempdir_str)
        repo = git.Repo.clone_from(repo_url, tempdir_str)
        for shed_yml_path in tempdir.glob('tools/**/.shed.y*ml', case_sensitive=False):
            if re.match(r'^.*\.ya?ml$', str(shed_yml_path).lower()):
                with shed_yml_path.open('r') as fp:
                    shed = yaml.safe_load(fp)
                repo_name = shed.get('name')
                repo_owner = shed.get('owner')
                if repo_name and repo_owner:
                    yield repo_name, repo_owner


def list_revisions(repo_name: str, repo_owner: str) -> list[str]:
    try:
        return ts.repositories.get_ordered_installable_revisions(repo_name, repo_owner)
    except Exception as e:
        print(e, file=sys.stderr)
        return list()


def build_tools_dict(repo_url: str, verbose: bool = False) -> dict:
    tools = list()
    for repo_name, repo_owner in list_tool_repositories(repo_url):
        tool_revisions = list_revisions(repo_name, repo_owner)
        if len(tool_revisions) > 0:
            tools.append(
                dict(
                    name=repo_name,
                    owner=repo_owner,
                    revisions=[tool_revisions[-1]],
                    tool_panel_section_label='GIA',
                ),
            )
            if verbose:
                print(f'{tools[-1]["owner"]}/{tools[-1]["name"]}: {tools[-1]["revisions"]}')
    tools.sort(key=lambda tool: tool['name'])
    return dict(
        tools=tools,

        # Keep the image small, don't install Conda dependencies, run the container with
        # `--priviledged` to employ Singularity constainers instead:
        install_tool_dependencies=False,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-url', type=str, default='https://github.com/BMCV/galaxy-image-analysis.git')
    parser.add_argument('tools_file', type=str)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    tools_dict = build_tools_dict(args.repo_url, verbose=args.verbose)
    with open(args.tools_file, 'w') as fp:
        yaml.dump(tools_dict, fp)
