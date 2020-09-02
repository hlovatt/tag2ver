#!/usr/bin/env python3
"""
See HELP_TEXT.
"""


__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__version__ = "v0.5.0: Add updateself to use README as help text"


__all__ = ['main']

import os
import subprocess
import sys

from pathlib import Path

from typing import Tuple, List


VERSION_NAME = '__version__'
HELP_TEXT = '''
Usage from *folder with git repository to tag and source files to version*:

  *  `tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release/commit Description."]`, 
  if `tag2ver.py` is executable and on execution path.
  *  `<tag2ver dir>.tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release/commit Description."]`,
  if `tag2ver.py` is executable but not on execution path.
  *  `python3 <tag2ver dir>.tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release/commit Description."]`.

Options:

  * `-h`, print this message (rest of command line ignored).
  * `-f`, force the given version even if it is not a single increment.

Version:

  * Must be a [semantic version](https://semver.org) with format `v<Major>.<Minor>.<Patch>`.
  * Must be a single increment from previous version, unless `-f` option given.
  * Use: `<tag2ver dir>.tag2ver.py -f v0.0.0 "Add initial tag and version."` 
  (or similar), for 1st release.

Description:

  * Description of the version: a single, short, < 50 characters, sentence with 
  an imperative mood (in quotes to allow spaces).

Actions:

  * Checks git repository exists.
  * Updates the `__version__` attribute of all the `py` and `pyi` file's in the 
  current directory and sub-directories with given version and given description 
  (`__version__` attribute must already exist).
  * Commits all modified files, included `py` and `pyi` files that have modified 
  `__version__` attribute, with given description.
  * Tags the repository with given version and given description.
  * If `remote` exists, pushes `origin` to `master`.

EG:

  * `<tag2ver dir>.tag2ver.py -h`, prints help.
  * `<tag2ver dir>.tag2ver.py -f v0.0.0 "Add initial tag and version."`, for 1st release.
  * `<tag2ver dir>.tag2ver.py v0.0.1 "Fix bugs, tag, and version."`, for 2nd release.
  * `<tag2ver dir>.tag2ver.py v0.1.0 "Add features, tag, and version."`, for 3rd release.
  * `<tag2ver dir>.tag2ver.py v1.0.0 "Make incompatible changes, tag, and version."`, 
  for 4th release.
  * Etc. for subsequent releases.
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
    )
    ensure(
        git_check_process.returncode == 0 and bool(git_check_process.stdout),
        f'Current directory, {os.getcwd()}, does not have a git repository with at least one file.',
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


def push_repository_if_remote_exists() -> None:
    git_check_remote_process = subprocess.run(
        ['git', 'ls-remote'],
        capture_output=True,
    )
    if git_check_remote_process.returncode == 0 and bool(git_check_remote_process.stdout):
        ensure_process('git', 'push', 'origin', 'master')


def main() -> None:
    ensure_git()
    forced_version = is_forced_and_ensure_args()
    version = sys.argv[2] if forced_version else sys.argv[1]
    ensure_version(forced_version, version)
    description = sys.argv[3] if forced_version else sys.argv[2]
    version_files(version, description)
    commit_files(description)
    tag_repository(version, description)
    push_repository_if_remote_exists()


if __name__ == '__main__':
    main()
