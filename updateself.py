"""
Update the HELP_TEXT in `tag2ver.py` from `README.md` and then calls `tag2ver` with given arguments.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT."
__repository__ = 'https://github.com/hlovatt/tag2ver'
__version__ = "0.6.2"

__all__ = ['main']

from pathlib import Path
from typing import List, TextIO

import tag2ver

HELP_TEXT = 'HELP_TEXT'
HELP_TEXT_START = f"{HELP_TEXT} = '''"
HELP_TEXT_END = "'''"
TAG2VER = 'tag2ver.py'
README = 'README.md'
README_HELP_TEXT_START = '## Help Text'


def consume_old_help_text(py_file: TextIO) -> None:
    for help_line in py_file:
        if help_line.startswith(HELP_TEXT_END):
            break
    else:
        assert False, f'End of file found before end of `{HELP_TEXT}` in `{TAG2VER}`.'


def append_new_help_text(new_py: List[str]) -> None:
    with Path(README).open() as readme_file:
        for readme_line in readme_file:
            if readme_line.startswith(README_HELP_TEXT_START):
                break
        else:
            assert False, f'End of file found before `{README_HELP_TEXT_START}` in `{README}`.'
        next(readme_file)  # Consume blank line.
        for new_help_line in readme_file:
            new_py.append(new_help_line)
    new_py.append(HELP_TEXT_END + '\n')


def update_help_text():
    py_path = Path(TAG2VER)
    new_py: List[str] = []
    help_text_found = False
    with py_path.open() as py_file:
        for py_line in py_file:
            new_py.append(py_line)
            if py_line.startswith(HELP_TEXT_START):
                help_text_found = True
                consume_old_help_text(py_file)
                append_new_help_text(new_py)
    assert help_text_found, f'No `{HELP_TEXT}` line in `{TAG2VER}`.'
    tag2ver.replace_file(py_path, new_py)


def main() -> None:
    update_help_text()
    tag2ver.main()


if __name__ == '__main__':
    main()
