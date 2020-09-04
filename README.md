# `tag2var`

Easy release management: file versioning, git commit, git tagging, git remote, and PyPI. 

The name `tag2var` is meant to convey that the utility does everything from 
git tagging to file versioning and all in between and either side. In particular: 
`tag2var` updates `py` and `pyi` file's `__version__` attribute with given incremented 
[semantic version](https://semver.org), 
updates `version` attribute of `setup.py` (if `setup` exists),
commits `*.py` and `*.pyi` (including `setup.py`) files with given description,
tags git repository with given version and given description, 
pushes to remote (if remote exists), and uploads to `PyPI` 
(if `setup` exists).

The whole program is in the single file, `tag2var.py`, (without any dependencies outside 
of Python3.6+) and therefore this file alone can be copied to install the utility. 
Alternatively:

    pip3 install tag2ver

## Help Text

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
