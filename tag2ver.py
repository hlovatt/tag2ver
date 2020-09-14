#!/usr/bin/env python3
"""
See `HELP_TEXT` below or (better) `README.md` file in `__repository__` for more info.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__repository__ = "https://github.com/hlovatt/tag2ver"
__version__ = "0.6.3"

__all__ = ['main']

import argparse
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
HELP_TEXT = 'Easy release management: file versioning, git commit, git tagging, and  optionally git remote and PyPI.'


def ensure(condition: bool, msg: str, parser: argparse.ArgumentParser):
    """Similar to `assert`, except that it prints the help message instead of a stack trace and is always enabled."""
    if condition:
        return
    parser.print_help(sys.stderr)
    print(file=sys.stderr)
    print(msg, file=sys.stderr)
    exit(1)


def ensure_process(parser: argparse.ArgumentParser, *cmd: str):
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    ensure(
        process.returncode == 0,
        f'Sub-process `{process.args}` returned {process.returncode}',
        parser,
    )
    return process


def ensure_git_exists(parser: argparse.ArgumentParser):
    git_check_process = subprocess.run(
        ['git', 'ls-files'],
        capture_output=True,
    )
    ensure(
        git_check_process.returncode == 0 and git_check_process.stdout,
        f'Current directory, {os.getcwd()}, does not have a git repository with at least one file.',
        parser,
    )


def parse_version(version: str, parser: argparse.ArgumentParser):
    version_match = VERSION_RE.match(version)
    ensure(
        bool(version_match),
        f'Given `{version}` not of form `<Major>.<Minor>.<Patch>` (RE is `{VERSION_RE}`).',
        parser,
    )
    return int(version_match.group('major')), int(version_match.group('minor')), int(version_match.group('patch'))


def ensure_tag_version_if_not_forced(
        major: int,
        minor: int,
        patch: int,
        forced_version: bool,
        parser: argparse.ArgumentParser
):
    if forced_version:
        return
    git_tag_list_process = ensure_process(parser, 'git', 'tag')
    last_version = ''  # Doesn't do anything other than keep PyCharm control flow happy!
    try:
        last_version = git_tag_list_process.stdout.split()[-1]
    except IndexError:
        ensure(
            False,  # Always causes error message to print and then exit program.
            f'No previous tags, perhaps `<tag2ver dir>.tag2ver.py -f v0.0.0 "Add initial tag and version."`?',
            parser
        )
    last_major, last_minor, last_patch = parse_version(last_version, parser)
    ensure(
        (major == last_major + 1 and minor == 0 and patch == 0) or
        (major == last_major and minor == last_minor + 1 and patch == 0) or
        (major == last_major and minor == last_minor and patch == last_patch + 1),
        f'{major}.{minor}.{patch} not a single increment from {last_version}.',
        parser,
    )


def replace_file(path: Path, new_text: List[str]):
    bak_path = path.with_suffix('.bak')
    path.rename(bak_path)
    path.write_text(''.join(new_text))
    bak_path.unlink()


def version_as_str(major: int, minor: int, patch: int):
    return str(major) + '.' + str(minor) + '.' + str(patch)


def version_setup_and_ensure_version_if_setup_exists(
        major: int,
        minor: int,
        patch: int,
        parser: argparse.ArgumentParser
):
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
                f'More than one "version" kwarg found in `{SETUP_NAME}` on line `{line}` (RE is `{SETUP_VERSION_RE}`).',
                parser,
            )
            if num_subs > 0:
                ensure(
                    not version_found,
                    (
                        f'2nd "version" kwarg line found in `{SETUP_NAME}`, '
                        f'2nd line is `{line}` (RE is `{SETUP_VERSION_RE}`).'
                    ),
                    parser,
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
                    ),
                    parser,
                )
            new_setup.append(new_line)
    ensure(
        version_found,
        f'No "version" line found in `{SETUP_NAME}` (RE is `{SETUP_VERSION_RE}`).',
        parser,
    )
    replace_file(SETUP_PATH, new_setup)


def version_files(major: int, minor: int, patch: int, parser: argparse.ArgumentParser):
    paths = list(Path().rglob("*.py"))
    paths.extend(Path().rglob("*.pyi"))
    for path in paths:
        if path == SETUP_PATH:  # Setup is a special case.
            continue
        with path.open() as file:
            text = file.read()
            ensure(
                f'\n{VERSION_ATTR}' in text,
                f'File `{path}` does not have a line beginning `{VERSION_ATTR}`.',
                parser,
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


def commit_files(description: str, parser: argparse.ArgumentParser):
    ensure_process(parser, 'git', 'commit', '-am', f'"{description}"')


def tag_repository(major: int, minor: int, patch: int, description: str, parser: argparse.ArgumentParser):
    ensure_process(parser, 'git', 'tag', '-a', f'{version_as_str(major, minor, patch)}', '-m', f'"{description}"')


def push_repository_if_remote_exists(major: int, minor: int, patch: int, parser: argparse.ArgumentParser):
    git_check_remote_process = subprocess.run(
        ['git', 'ls-remote'],
        capture_output=True,
    )
    if git_check_remote_process.returncode == 0 and bool(git_check_remote_process.stdout):
        ensure_process(parser, 'git', 'push', '--atomic', 'origin', 'master', version_as_str(major, minor, patch))


def publish_to_pypi_if_setup_exists():
    if not SETUP_PATH.is_file():
        return


def parse_args():
    parser = argparse.ArgumentParser(description=HELP_TEXT, epilog=f'For more information see: {__repository__}.')
    parser.add_argument('-f', '--force', help='force tagging/versioning even if out of sequence', action='store_true')
    parser.add_argument('version', help='tag/version number in format: `<Major>.<Minor>.<Patch>`')
    parser.add_argument('description', help='description of tag/commit')
    return parser, parser.parse_args()


def main():
    parser, args = parse_args()
    ensure_git_exists(parser)
    forced_version, version, description = args.force, args.version, args.description
    major, minor, patch = parse_version(version, parser)
    ensure_tag_version_if_not_forced(major, minor, patch, forced_version, parser)
    version_setup_and_ensure_version_if_setup_exists(major, minor, patch, parser)
    version_files(major, minor, patch, parser)
    commit_files(description, parser)
    tag_repository(major, minor, patch, description, parser)
    push_repository_if_remote_exists(major, minor, patch, parser)
    publish_to_pypi_if_setup_exists()


if __name__ == '__main__':
    main()
