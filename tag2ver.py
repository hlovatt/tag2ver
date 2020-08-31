#!/usr/bin/env python3
"""
Tag git repository with incremented [semantic version](https://semver.org) and
update `py` and `pyi` file's `__version__` to tag.
"""
import subprocess
import sys

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__version__ = "v0.1.2: Features complete release and committed to repository."

from pathlib import Path

from typing import Tuple, List


def print_help_msg() -> None:
    print('''
Usage from directory with git repository to be tagged and source files to update:
  *  tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release Description."]`, if `tag2ver.py` is executable 
  and on execution path.
  *  `<tag2ver dir>.tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release Description."]`, if `tag2ver.py` is 
  executable but not on execution path.
  *  `python3 <tag2ver dir>.tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release Description."]`.
Options:
  * `-h`, print this message (rest of command line ignored).
  * `-f`, force the given version even if it is not a single increment.
Version:
  * Must be a [semantic version](https://semver.org) with format `v<Major>.<Minor>.<Patch>`.
  * Must be a single increment from previous version, unless `-f` option given.
  * Use `<tag2ver dir>.tag2ver.py -f v0.0.0 "Initial release."`, for 1st release.
Description:
  * Description of the version, normally a single short sentence (typically in quotes to allow spaces).
Actions:
  * Tags the repository with the version and description.
  * Updates the `__version__` attribute of all the `py` and `pyi` file's in the current directory and sub-directories,
  `__version__` attribute must already exist.
EG:
  * `<tag2ver dir>.tag2ver.py -h`, prints help.
  * `<tag2ver dir>.tag2ver.py -f v0.0.0 "Initial release."`, for 1st release.
  * `<tag2ver dir>.tag2ver.py v0.0.1 "Bug fixes release."`, for 2nd release.
  * `<tag2ver dir>.tag2ver.py v0.1.0 "New features release."`, for 3rd release.
  * `<tag2ver dir>.tag2ver.py v1.0.0 "Incompatible changes release."`, for 4th release.
  * Etc. for subsequent releases.
''')


def ensure(condition: bool, msg: str) -> None:
    """Similar to `assert`, except that it prints the help message instead of a stack trace and is always enabled."""
    if condition:
        return
    print_help_msg()
    print()
    print(msg)
    exit(1)


def is_forced_and_ensure_args() -> bool:
    args = sys.argv
    num_args = len(args)
    ensure(
        num_args > 1 and args[1] != '-h',
        ''
    )
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
    git_tag_list_process = subprocess.run(['git', 'tag'], stdout=subprocess.PIPE, text=True)
    git_tag_list_process.check_returncode()
    last_version = ''  # Doesn't do anything other than keep PyCharm control flow happy!
    try:
        last_version = git_tag_list_process.stdout.split()[-1]
    except IndexError:
        ensure(
            False,  # Always causes error message to print and then exit program.
            f'No previous tags in repository, perhaps `<tag2ver dir>.tag2ver.py -f v0.0.0 "Initial release."`?'
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
        new_file: List[str] = []
        with file.open() as f:
            version_line = False
            for line in f:
                if line.startswith('__version__'):
                    if version_line:
                        ensure(
                            False,  # Force error message, help text, and exit.
                            f'File `{file}` has more than one line beginning `__version__`.'
                        )
                    version_line = True
                    new_file.append(f'__version__ = "{version}: {description}"\n')
                else:
                    new_file.append(line)
            ensure(
                version_line,
                f'File `{file}` does not have a line beginning `__version__`.'
            )
        bak_path = Path(str(file) + '.bak')
        file.rename(bak_path)
        file.write_text(''.join(new_file))
        bak_path.unlink()


def version_repository(version: str, description: str) -> None:
    git_new_tag_process = subprocess.run(
        ['git', 'tag', '-a', f'{version}', '-m', f'"{description}"'],
        stdout=subprocess.PIPE,
        text=True
    )
    git_new_tag_process.check_returncode()


def main() -> None:
    forced_version = is_forced_and_ensure_args()
    version = sys.argv[2] if forced_version else sys.argv[1]
    ensure_version(forced_version, version)
    description = sys.argv[3] if forced_version else sys.argv[2]
    version_files(version, description)
    version_repository(version, description)


if __name__ == '__main__':
    main()
