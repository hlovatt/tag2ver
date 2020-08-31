#!/usr/bin/env python3
"""
Tag git repository with incremented [semantic version](https://semver.org) and
update `py` and `pyi` file's `__version__` to tag.
"""
import subprocess
import sys


def print_help_msg() -> None:
    print('''
Usage from directory with git repository to be tagged and source files to update:
  *  tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release Description."]`, if `tag2ver.py` is executable 
  and on execution path.
  *  `<tag2ver dir>.tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release Description."]`, if `tag2ver.py` is 
  executable but not on execution path.
  *  `python3 <tag2ver dir>.tag2ver.py [options] [v<Major>.<Minor>.<Patch> "Release Description."]`.
EG:
  * `<tag2ver dir>.tag2ver.py -h`, prints help.
  * `<tag2ver dir>.tag2ver.py -f v0.0.0 "Initial release."`, for 1st release.
  * `<tag2ver dir>.tag2ver.py v0.0.1 "Bug fixes release."`, for 2nd release.
  * `<tag2ver dir>.tag2ver.py v0.1.0 "New features release."`, for 3rd release.
  * `<tag2ver dir>.tag2ver.py v1.0.0 "Incompatible changes release."`, for 4th release.
  * Etc. for subsequent releases.
Options:
  * `-h`, print this message (rest of command line ignored).
  * `-f`, force the given version even if it is not a single increment.
Version:
  * Must be a [semantic version](https://semver.org) with format `v<Major>.<Minor>.<Patch>`.
  * Must be a single increment from previous version unless `-f` option given.
  * Use `<tag2ver dir>.tag2ver.py -f v0.0.0 "Initial release."`, for 1st release.
Description:
  * Description of the version, normally a single short sentence (typically in quotes to allow spaces).
Actions:
  * Tags the repository with the version and description.
  * Updates the `__version__` attribute of all the `py` and `pyi` file's in the current directory and sub-directories.
  * If `__version__` does not exist in a source file it is created.
''')


def is_forced_and_check_args() -> bool:
    args = sys.argv
    num_args = len(args)
    if num_args < 2 or args[1] == '-h':
        print_help_msg()
        exit()
    if args[1][0] == '-' and args[1] != '-f':
        print(f'''
Option, {args[1]}, not understood, must be: absent, `-h`, or `-f`.
''')
        print_help_msg()
        exit()
    if args[1] == '-f':
        if num_args != 4:
            print(f'''
`-f` option must be followed by both 'version' and 'description'.
''')
            print_help_msg()
            exit()
        return True
    if num_args != 3:
        print(f'''
Both 'version' and 'description' must be given.
''')
        print_help_msg()
        exit()
    return False


def check_version(force_version: bool, version: str) -> None:
    git_tags_process = subprocess.run(['git', 'tag'], stdout=subprocess.PIPE, universal_newlines=True)
    print(git_tags_process)


def main() -> None:
    force_version = is_forced_and_check_args()
    version = sys.argv[2] if force_version else sys.argv[1]
    check_version(force_version, version)
    description = sys.argv[3] if force_version else sys.argv[2]
    print(version)
    print(description)


if __name__ == '__main__':
    main()
