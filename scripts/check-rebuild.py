import argparse
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tools_file', type=str)
    args = parser.parse_args()

    result = subprocess.run(
        ['git', 'diff', args.tools_file],
        capture_output=True,
        text=True,
        check=False,  # git diff returns 1 when differences exist
    )
    print('true' if result.stdout else 'false')
