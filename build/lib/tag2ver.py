#!/usr/bin/env python3
"""
Easy release management: file versioning, git commit, git tagging, git remote, and PyPI.
See `HELP_TEXT` below or `README.md` file for more info.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__repository__ = "https://github.com/hlovatt/tag2ver"
__version__ = "0.6.11"

__all__ = ['main', 'replace_file']

import os
import re
import subprocess
import sys

from pathlib import Path

from typing import List

VERSION_RE_STR = r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
VERSION_RE = re.compile(r'^' + VERSION_RE_STR + r'$')
VERSION_ATTR = '__version__'
SETUP_NAME = 'setup.py'
SETUP_PATH = Path(SETUP_NAME)
SETUP_VERSION_RE = re.compile(r'(?P<attr>version\s*=\s*)(?P<quote>["|' + r"'])" + VERSION_RE_STR + r'(?P=quote)')
HELP_TEXT = '''
Usage from *folder with git repository to tag and source files to version*:

  *  `tag2ver.py [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]`, 
  if `tag2ver.py` is executable and on execution path.
  *  `<tag2ver dir>.tag2ver.py [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]`,
  if `tag2ver.py` is executable but not on execution path.
  *  `python3 <tag2ver dir>.tag2ver.py [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]`.

Options:

  * `-h`, print this message (rest of command line ignored).
  * `-f`, force the given git version (not PyPI) even if it is not a single increment.

Version:

  * Must be a [semantic version](https://semver.org) with format `<Major>.<Minor>.<Patch>`.
  * Must be a single increment from previous git tag version, unless `-f` option given.
  * Must be at least one increment from PyPI version (if PyPI used, `-f` not considered).
  * Use: `<tag2ver dir>.tag2ver.py -f 0.0.0 "Add initial tag and version."` 
  (or similar), for 1st tagging in repository.

Description:

  * Description of the version: a single, short, < 50 characters, sentence with 
  an imperative mood (in quotes to allow spaces).

Actions:

  * Checks git repository exists.
  * Checks version number is *a* single increment from last git tag (except `-f` option) 
  and of form `<Major>.<Minor>.<Patch>` and description exists.
  * Checks if PyPI deployed (`setup.py` must exist).
    * Checks version number is at least one increment from last PyPI deployment 
    (regardless of `-f` option).
    * Updates `setup.py`'s `version` attribute with given version 
    (`version` attribute must already exist).
  * Updates the `__version__` attribute of all the `py` and `pyi` file's in the 
  current directory and sub-directories with given version 
  (`__version__` attribute must already exist).
  * Commits all modified files, including `py` and `pyi` files that have been modified, 
  with given description.
  * Tags the repository with given version and given description.
  * If `remote` repository exists, pushes `origin` to `master`.
  * If `setup.py` exists, uploads to `PyPI` with given version.

EG:

  * `<tag2ver dir>.tag2ver.py -h`, prints help.
  * `<tag2ver dir>.tag2ver.py -f 0.0.0 "Add initial tag and version."`, for 1st release.
  * `<tag2ver dir>.tag2ver.py 0.0.1 "Fix bugs, tag, and version."`, for 2nd release.
  * `<tag2ver dir>.tag2ver.py 0.1.0 "Add features, tag, and version."`, for 3rd release.
  * `<tag2ver dir>.tag2ver.py 1.0.0 "Make incompatible changes, tag, and version."`, 
  for 4th release.
  * Etc. for subsequent releases.
'''


def ensure(condition: bool, msg: str):
    """Similar to `assert`, except that it prints the help message instead of a stack trace and is always enabled."""
    if condition:
        return
    print(HELP_TEXT, file=sys.stderr)
    print(file=sys.stderr)
    print(msg, file=sys.stderr)
    exit(1)


def ensure_process(*cmd: str):
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


def ensure_git_exists():
    git_check_process = subprocess.run(
        ['git', 'ls-files'],
        capture_output=True,
    )
    ensure(
        git_check_process.returncode == 0 and git_check_process.stdout,
        f'Current directory, {os.getcwd()}, does not have a git repository with at least one file.',
    )


def is_forced_and_ensure_args():
    args = sys.argv
    num_args = len(args)
    if num_args < 2 or args[1] == '-h':
        print(HELP_TEXT)
        exit(0)
    ensure(
        args[1][0] != '-' or args[1] == '-f',
        f'Option, {args[1]}, not understood, must be: absent, `-h`, or `-f`.'
    )
    if args[1] == '-f':
        ensure(
            num_args == 4,
            f"`-f` option must be followed by both 'version' and 'description' (and nothing else)."
        )
        return True
    ensure(
        num_args == 3,
        f"Both 'version' and 'description' must be given (and nothing else if no options)."
    )
    return False


def parse_version(version: str):
    version_match = VERSION_RE.match(version)
    ensure(
        bool(version_match),
        f'Given `{version}` not of form `<Major>.<Minor>.<Patch>` (RE is `{VERSION_RE}`).'
    )
    return int(version_match.group('major')), int(version_match.group('minor')), int(version_match.group('patch'))


def ensure_tag_version_if_not_forced(major: int, minor: int, patch: int, forced_version: bool):
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
    last_major, last_minor, last_patch = parse_version(last_version)
    ensure(
        (major == last_major + 1 and minor == 0 and patch == 0) or
        (major == last_major and minor == last_minor + 1 and patch == 0) or
        (major == last_major and minor == last_minor and patch == last_patch + 1),
        f'{major}.{minor}.{patch} not a single increment from {last_version}.'
    )


def replace_file(path: Path, new_text: List[str]):
    bak_path = path.with_suffix('.bak')
    path.rename(bak_path)
    path.write_text(''.join(new_text))
    bak_path.unlink()


def version_as_str(major: int, minor: int, patch: int):
    return str(major) + '.' + str(minor) + '.' + str(patch)


def version_setup_and_ensure_version_if_setup_exists(major: int, minor: int, patch: int):
    if not SETUP_PATH.is_file():
        return
    sub_str = r'\g<attr>\g<quote>' + version_as_str(major, minor, patch) + r'\g<quote>'
    version_found = False
    new_setup: List[str] = []
    with SETUP_PATH.open() as setup_lines:
        for line in setup_lines:
            new_line, num_subs = SETUP_VERSION_RE.subn(sub_str, line)
            ensure(
                num_subs < 2,
                f'More than one "version" kwarg found in `{SETUP_NAME}` on line `{line}` (RE is `{SETUP_VERSION_RE}`).'
            )
            if num_subs > 0:
                ensure(
                    not version_found,
                    (
                        f'2nd "version" kwarg line found in `{SETUP_NAME}`, '
                        f'2nd line is `{line}` (RE is `{SETUP_VERSION_RE}`).'
                    )
                )
                version_found = True
                matched_version = SETUP_VERSION_RE.search(line)
                pypi_major = int(matched_version.group('major'))
                pypi_minor = int(matched_version.group('minor'))
                pypi_patch = int(matched_version.group('patch'))
                ensure(
                    (major > pypi_major)
                    or
                    (major == pypi_major and minor > pypi_minor)
                    or
                    (major == pypi_major and minor == pypi_minor and patch > pypi_patch),
                    (
                        f'Given version `{major}.{minor}.{patch}` not greater than '
                        f'PyPI version `{pypi_major}.{pypi_minor}.{pypi_patch}`.'
                    )
                )
            new_setup.append(new_line)
    ensure(
        version_found,
        f'No "version" line found in `{SETUP_NAME}` (RE is `{SETUP_VERSION_RE}`).'
    )
    replace_file(SETUP_PATH, new_setup)


def version_files(major: int, minor: int, patch: int):
    paths = list(Path().rglob("*.py"))
    paths.extend(Path().rglob("*.pyi"))
    for path in paths:
        if path == SETUP_PATH:  # Setup is a special case.
            continue
        with path.open() as file:
            text = file.read()
            ensure(
                f'\n{VERSION_ATTR}' in text,
                f'File `{path}` does not have a line beginning `{VERSION_ATTR}`.'
            )
    for path in paths:
        new_file: List[str] = []
        with path.open() as file:
            for line in file:
                if line.startswith(VERSION_ATTR):
                    new_file.append(f'{VERSION_ATTR} = "{version_as_str(major, minor, patch)}"\n')
                else:
                    new_file.append(line)
        replace_file(path, new_file)


def commit_files(description: str):
    ensure_process('git', 'commit', '-am', f'"{description}"')


def tag_repository(major: int, minor: int, patch: int, description: str):
    ensure_process('git', 'tag', '-a', f'{version_as_str(major, minor, patch)}', '-m', f'"{description}"')


def push_repository_if_remote_exists(major: int, minor: int, patch: int):
    git_check_remote_process = subprocess.run(
        ['git', 'ls-remote'],
        capture_output=True,
    )
    if git_check_remote_process.returncode == 0 and bool(git_check_remote_process.stdout):
        ensure_process('git', 'push', '--atomic', 'origin', 'master', version_as_str(major, minor, patch))


def publish_to_pypi_if_setup_exists():
    if not SETUP_PATH.is_file():
        return


def main():
    ensure_git_exists()
    forced_version = is_forced_and_ensure_args()
    version = sys.argv[2] if forced_version else sys.argv[1]
    major, minor, patch = parse_version(version)
    ensure_tag_version_if_not_forced(major, minor, patch, forced_version)
    version_setup_and_ensure_version_if_setup_exists(major, minor, patch)
    version_files(major, minor, patch)
    description = sys.argv[3] if forced_version else sys.argv[2]
    commit_files(description)
    tag_repository(major, minor, patch, description)
    push_repository_if_remote_exists(major, minor, patch)
    publish_to_pypi_if_setup_exists()


if __name__ == '__main__':
    main()
