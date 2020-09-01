#!/usr/bin/env python3
"""
See HELP_TEXT.
"""


__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__version__ = "v0.3.0: Add commit after versioning and errors go to stderr"


__all__ = ['main']

import os
import subprocess
import sys

from pathlib import Path

from typing import Tuple, List


VERSION_NAME = '__version__'
HELP_TEXT = '''
'''


def print_help_msg(file=sys.stdout) -> None:
    print(HELP_TEXT, file=file)


def ensure(condition: bool, msg: str) -> None:
    """Similar to `assert`, except that it prints the help message instead of a stack trace and is always enabled."""
    if condition:
        return
    print_help_msg(file=sys.stderr)
    print(file=sys.stderr)
    print(msg, file=sys.stderr)
    exit(1)


def ensure_process(*cmd: str) -> subprocess.CompletedProcess:
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    ensure(
        process.returncode == 0,
        f'Sub-process `{process.args}` returned {process.returncode}',
    )
    return process


def ensure_git() -> None:
    git_check_process = subprocess.run(
        ['git', 'ls-files'],
        capture_output=True,
        text=True,
    )
    ensure(
        bool(git_check_process.stdout),
        f'Current directory, {os.getcwd()}, does not have a git repository.',
    )


def is_forced_and_ensure_args() -> bool:
    args = sys.argv
    num_args = len(args)
    if num_args < 2 or args[1] == '-h':
        print_help_msg()
        exit(0)
    ensure(
        args[1][0] != '-' or args[1] == '-f',
        f'Option, {args[1]}, not understood, must be: absent, `-h`, or `-f`.'
    )
    if args[1] == '-f':
        ensure(
            num_args == 4,
            f"`-f` option must be followed by both 'version' and 'description'."
        )
        return True
    ensure(
        num_args == 3,
        f"Both 'version' and 'description' must be given."
    )
    return False


def part_version(version: str, name: str, start: int = 0, patch: bool = False) -> Tuple[int, int]:
    dot_idx = 0 if patch else version.find('.', start + 1)
    ensure(
        patch or dot_idx > start,
        f"{name} number not found in `{version}`, index of dot separator is {dot_idx} which must be `> {start}`."
    )
    part = 0  # Doesn't do anything, other than keeping PyCharm flow checker happy!
    try:
        part = int(version[start + 1:]) if patch else int(version[start + 1:dot_idx])
    except ValueError as e:
        ensure(
            False,  # Always causes an exit with help message.
            f'{name} number in `{version}` is not a valid integer, error is `{e}`.'
        )
    return part, dot_idx


def scan_version(version: str) -> Tuple[int, int, int]:
    ensure(
        version[0] == 'v',
        f"'version' must begin with 'v', begins with `{version[0]}`."
    )
    major, minor_dot_idx = part_version(version, 'Major')
    minor, patch_dot_idx = part_version(version, 'Minor', minor_dot_idx)
    patch, _ = part_version(version, 'Patch', patch_dot_idx, patch=True)
    return major, minor, patch


def ensure_version(forced_version: bool, version: str) -> None:
    major, minor, patch = scan_version(version)
    if forced_version:
        return
    git_tag_list_process = ensure_process('git', 'tag')
    last_version = ''  # Doesn't do anything other than keep PyCharm control flow happy!
    try:
        last_version = git_tag_list_process.stdout.split()[-1]
    except IndexError:
        ensure(
            False,  # Always causes error message to print and then exit program.
            f'No previous tags, perhaps `<tag2ver dir>.tag2ver.py -f v0.0.0 "Add initial tag and version."`?'
        )
    last_major, last_minor, last_patch = scan_version(last_version)
    ensure(
        (major == last_major + 1 and minor == 0 and patch == 0) or
        (major == last_major and minor == last_minor + 1 and patch == 0) or
        (major == last_major and minor == last_minor and patch == last_patch + 1),
        f'{version} not a single increment from {last_version}.'
    )


def version_files(version: str, description: str) -> None:
    files = list(Path().rglob("*.py"))
    files.extend(Path().rglob("*.pyi"))
    for file in files:
        with file.open() as f:
            text = f.read()
            ensure(
                f'\n{VERSION_NAME}' in text,
                f'File `{file}` does not have a line beginning `{VERSION_NAME}`.'
            )
    for file in files:
        new_file: List[str] = []
        with file.open() as f:
            for line in f:
                if line.startswith(VERSION_NAME):
                    new_file.append(f'{VERSION_NAME} = "{version}: {description}"\n')
                else:
                    new_file.append(line)
        bak_path = Path(str(file) + '.bak')
        file.rename(bak_path)
        file.write_text(''.join(new_file))
        bak_path.unlink()


def commit_files(description: str) -> None:
    ensure_process('git', 'commit', '-am', f'"{description}"')


def tag_repository(version: str, description: str) -> None:
    ensure_process('git', 'tag', '-a', f'{version}', '-m', f'"{description}"')


def main() -> None:
    ensure_git()
    forced_version = is_forced_and_ensure_args()
    version = sys.argv[2] if forced_version else sys.argv[1]
    ensure_version(forced_version, version)
    description = sys.argv[3] if forced_version else sys.argv[2]
    version_files(version, description)
    commit_files(description)
    tag_repository(version, description)


if __name__ == '__main__':
    main()
