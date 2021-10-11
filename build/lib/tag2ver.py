#!/usr/bin/env python3
"""
See `HELP_TEXT` below or (better) `README.md` file in `__repository__` for more info.
"""

__author__ = "Howard C Lovatt."
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__repository__ = "https://github.com/hlovatt/tag2ver"
__version__ = "1.2.1"  # Version set by https://github.com/hlovatt/tag2ver

__all__ = ["main"]

import argparse
import os
import re
import subprocess
import sys

from pathlib import Path

from typing import List, Callable, Iterable, Final

VERSION_RE_STR: Final = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
VERSION_RE: Final = re.compile(r"^" + VERSION_RE_STR + r"$")
VERSION_ATTR: Final = "__version__"
SETUP_NAME: Final = "setup.py"
SETUP_PATH: Final = Path(SETUP_NAME)
SETUP_VERSION_RE: Final = re.compile(
    r'(?P<attr>version\s*=\s*)(?P<quote>["|' + r"'])" + VERSION_RE_STR + r"(?P=quote)"
)
HELP_TEXT: Final = "Easy release management: file versioning, git commit, git tagging, and optionally git remote and PyPI."
DIST_PATH: Final = Path("dist")
DIST_PATTERN: Final = str(DIST_PATH / "*")
PARSER: Final = argparse.ArgumentParser(
    description=HELP_TEXT, epilog=f"For more information see: {__repository__}."
)
EXCLUDE_PATHS: Final = [Path("build"), DIST_PATH, Path("media"), Path("venv")]


def ensure(condition: bool, msg: str, *, rollback: Callable[[], None] = lambda: None):
    """Similar to `assert`, except that it prints the help message instead of a stack trace and is always enabled."""
    if condition:
        return
    rollback()
    PARSER.print_help(sys.stderr)
    print(file=sys.stderr)
    print(msg, file=sys.stderr)
    exit(1)


def ensure_process(*cmd: str, rollback: Callable[[], None] = lambda: None):
    process = subprocess.run(cmd, capture_output=True, text=True,)
    ensure(
        process.returncode == 0,
        f"Sub-process `{process.args}` failed with exit code {process.returncode} and error message `{process.stdout}`",
        rollback=rollback,
    )
    return process


def ensure_git_exists():
    git_check_process = subprocess.run(["git", "ls-files"], capture_output=True,)
    ensure(
        git_check_process.returncode == 0 and git_check_process.stdout,
        f"Current directory, {os.getcwd()}, does not have a git repository with at least one file.",
    )


def parse_version(version: str):
    version_match = VERSION_RE.match(version)
    ensure(
        bool(version_match),
        f"Given `{version}` not of form `<Major>.<Minor>.<Patch>` (RE is `{VERSION_RE}`).",
    )
    return (
        int(version_match.group("major")),
        int(version_match.group("minor")),
        int(version_match.group("patch")),
    )


def ensure_tag_version_if_not_forced(
    major: int, minor: int, patch: int, forced_version: bool,
):
    if forced_version:
        return
    git_tag_list_process: Final = ensure_process("git", "tag")
    last_version = ""  # Doesn't do anything other than keep PyCharm control flow happy!
    try:
        versions: Final = git_tag_list_process.stdout.split()
        versions.sort(key=parse_version)
        last_version = versions[-1]
    except IndexError:
        ensure(
            False,  # Always causes error message to print and then exit program.
            f'No previous tags, perhaps `<tag2ver dir>.tag2ver.py -f 0.0.0 "Add initial tag and version."`?',
        )
    last_major, last_minor, last_patch = parse_version(last_version)
    ensure(
        (major == last_major + 1 and minor == 0 and patch == 0)
        or (major == last_major and minor == last_minor + 1 and patch == 0)
        or (major == last_major and minor == last_minor and patch == last_patch + 1),
        f"{version_as_str(major, minor, patch)} not a single increment from {last_version}.",
    )


def make_bak_path(path: Path):
    return path.with_suffix(".bak")


def replace_file(path: Path, new_text: List[str]):
    bak_path: Final = make_bak_path(path)
    path.rename(bak_path)
    path.write_text("".join(new_text))
    bak_path.unlink()


def version_as_str(major: int, minor: int, patch: int):
    return f"{major}.{minor}.{patch}"


def dist_files():
    return set(DIST_PATH.iterdir())


def ensure_setup_version_and_version_setup_if_setup_exists(
    major: int, minor: int, patch: int, args: argparse.Namespace,
):
    if not SETUP_PATH.is_file():
        ensure(
            not args.test_pypi,
            "`Test PyPI specified but no `" + SETUP_NAME + "` file!",
        )
        return
    sub_str: Final = r"\g<attr>\g<quote>" + version_as_str(
        major, minor, patch
    ) + r"\g<quote>"
    version_found = False
    new_setup: Final[List[str]] = []
    with SETUP_PATH.open() as setup_lines:
        for line in setup_lines:
            new_line, num_subs = SETUP_VERSION_RE.subn(sub_str, line)
            ensure(
                num_subs < 2,
                f'More than one "version" kwarg found in `{SETUP_NAME}` on line `{line}` (RE is `{SETUP_VERSION_RE}`).',
            )
            if num_subs > 0:
                ensure(
                    not version_found,
                    (
                        f'2nd "version" kwarg line found in `{SETUP_NAME}`, '
                        f"2nd line is `{line}` (RE is `{SETUP_VERSION_RE}`)."
                    ),
                )
                version_found = True
                matched_version = SETUP_VERSION_RE.search(line)
                pypi_major = int(matched_version.group("major"))
                pypi_minor = int(matched_version.group("minor"))
                pypi_patch = int(matched_version.group("patch"))
                ensure(
                    (major > pypi_major)
                    or (major == pypi_major and minor > pypi_minor)
                    or (
                        major == pypi_major
                        and minor == pypi_minor
                        and patch > pypi_patch
                    ),
                    (
                        f"Given version, `{version_as_str(major, minor, patch)}`, not greater than "
                        f"PyPI version, `{version_as_str(pypi_major, pypi_minor, pypi_patch)}`."
                    ),
                )
            new_setup.append(new_line)
    ensure(
        version_found,
        f'No "version" line found in `{SETUP_NAME}` (RE is `{SETUP_VERSION_RE}`).',
    )
    replace_file(SETUP_PATH, new_setup)


def not_excluded_dir(path: Path):
    parents: Final = list(path.parents)
    if len(parents) < 2:
        return True
    root_parent = parents[-2]
    return not (root_parent in EXCLUDE_PATHS) and not (
        root_parent.suffix == ".egg_info"
    )


def filter_build_etc_dirs(paths: Iterable[Path]):
    return (path for path in paths if not_excluded_dir(path))


def version_files(major: int, minor: int, patch: int):
    paths: Final = list(filter_build_etc_dirs(Path().rglob("*.py")))
    paths.extend(filter_build_etc_dirs(Path().rglob("*.pyi")))
    for path in paths:
        if path == SETUP_PATH:  # Setup is a special case.
            continue
        with path.open() as file:
            text = file.read()
            ensure(
                f"\n{VERSION_ATTR}" in text,
                f"File `{path}` does not have a line beginning `{VERSION_ATTR}`.",
            )
    for path in paths:
        new_file: List[str] = []
        with path.open() as file:
            for line in file:
                if line.startswith(VERSION_ATTR):
                    new_file.append(
                        f'{VERSION_ATTR} = "{version_as_str(major, minor, patch)}"  # Version set by {__repository__}\n'
                    )
                else:
                    new_file.append(line)
        replace_file(path, new_file)


def commit_files(description: str):
    ensure_process("git", "commit", "-am", f'"{description}"')


def tag_repository(major: int, minor: int, patch: int, description: str):
    ensure_process(
        "git",
        "tag",
        "-a",
        f"{version_as_str(major, minor, patch)}",
        "-m",
        f'"{description}"',
    )


def push_repository_if_remote_exists(major: int, minor: int, patch: int):
    git_check_remote_process: Final = subprocess.run(
        ["git", "ls-remote"], capture_output=True
    )
    if git_check_remote_process.returncode == 0 and bool(
        git_check_remote_process.stdout
    ):
        ensure_process(
            "git",
            "push",
            "--atomic",
            "origin",
            "master",
            version_as_str(major, minor, patch),
        )


def publish_to_pypi_if_setup_exists(args: argparse.Namespace):
    if not SETUP_PATH.is_file():
        return
    repository: Final = ["--repository", "testpypi"] if args.test_pypi else []
    username: Final = ["--username", args.username] if args.username else []
    password: Final = ["--password", args.password] if args.password else []
    ensure_process(
        "python3",
        "-m",
        "twine",
        "upload",
        *repository,
        *username,
        *password,
        DIST_PATTERN,
    )


def create_new_pypi_files_and_delete_old_files_if_any_and_if_setup_exists():
    if not SETUP_PATH.is_file():
        return
    if DIST_PATH.is_dir():
        ensure_process("git", "rm", DIST_PATTERN)
    ensure_process("python3", SETUP_NAME, "sdist", "bdist_wheel")
    ensure_process("git", "add", DIST_PATTERN)


def save_existing_pypi_files_if_any():
    if not DIST_PATH.is_dir():
        return  # No existing PyPI files.
    DIST_PATH.rename(make_bak_path(DIST_PATH))


def delete_temp_pypi_files_and_restore_existing_files_if_any():
    for created_file in DIST_PATH.iterdir():
        created_file.unlink()
    DIST_PATH.rmdir()
    bak_dist_path: Final = make_bak_path(DIST_PATH)
    if bak_dist_path.is_dir():
        make_bak_path(DIST_PATH).rename(DIST_PATH)


def ensure_pypi_check_if_setup_exists():
    if not SETUP_PATH.is_file():
        return
    ensure_process(
        "python3",
        "-m",
        "pip",
        "install",
        "--user",
        "--upgrade",
        "pip",
        "setuptools",
        "wheel",
        "twine",
    )
    save_existing_pypi_files_if_any()
    ensure_process(
        "python3",
        SETUP_NAME,
        "sdist",
        "bdist_wheel",
        rollback=delete_temp_pypi_files_and_restore_existing_files_if_any,
    )
    ensure_process(
        "python3",
        "-m",
        "twine",
        "check",
        DIST_PATTERN,
        rollback=delete_temp_pypi_files_and_restore_existing_files_if_any,
    )
    delete_temp_pypi_files_and_restore_existing_files_if_any()


def parse_args():
    PARSER.add_argument(
        "-V",
        "--version",
        help="show program's version number and exit",
        action="version",
        version="%(prog)s " + __version__,
    )
    PARSER.add_argument(
        "-f",
        "--force_tag",
        help="force tag version even if out of sequence",
        action="store_true",
    )
    PARSER.add_argument(
        "tag_version",
        help="tag and file version number in format: `<Major>.<Minor>.<Patch>`",
    )
    PARSER.add_argument("tag_description", help="description for tag and commit")
    PARSER.add_argument(
        "-t",
        "--test_pypi",
        help=(
            "use `Test PyPI` instead of `PyPI` "
            "(passes `--repository testpypi` onto twine (https://twine.readthedocs.io/en/latest/)."
        ),
        action="store_true",
    )
    PARSER.add_argument(
        "-u",
        "--username",
        help=(
            "username for `PyPI`/`Test PyPI` "
            "(passed onto twine (https://twine.readthedocs.io/en/latest/)."
        ),
    )
    PARSER.add_argument(
        "-p",
        "--password",
        help=(
            "password for `PyPI`/`Test PyPI` "
            "(passed onto twine (https://twine.readthedocs.io/en/latest/)."
        ),
    )
    return PARSER.parse_args()


def format_with_black_if_installed():
    black_check: Final = subprocess.run(
        ["black", "--version"], capture_output=True, text=True,
    )
    if black_check.returncode != 0:
        return
    ensure_process("black", ".")


def main():
    format_with_black_if_installed()
    ensure_git_exists()
    args: Final = parse_args()
    forced_version, version, description = (
        args.force_tag,
        args.tag_version,
        args.tag_description,
    )
    major, minor, patch = parse_version(version)
    ensure_tag_version_if_not_forced(major, minor, patch, forced_version)
    ensure_pypi_check_if_setup_exists()
    ensure_setup_version_and_version_setup_if_setup_exists(major, minor, patch, args)
    version_files(major, minor, patch)
    create_new_pypi_files_and_delete_old_files_if_any_and_if_setup_exists()
    commit_files(description)
    tag_repository(major, minor, patch, description)
    push_repository_if_remote_exists(major, minor, patch)
    publish_to_pypi_if_setup_exists(args)


if __name__ == "__main__":
    main()
