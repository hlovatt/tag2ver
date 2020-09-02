# `tag2var`

`tag2var` updates `py` and `pyi` file's `__version__` attribute with given incremented 
[semantic version](https://semver.org) and given description, 
commits `py` and `pyi` with given description,
tags git repository with given version and given description, and
pushes to remote (if remote exists).

The name `tag2var` is meant to convey that the utility does everything from 
git tagging to file versioning and all in between. The whole program is in the single
file `tag2var.py` and this file alone can be copied to install the utility.

## Help Text

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

EG:

  * `<tag2ver dir>.tag2ver.py -h`, prints help.
  * `<tag2ver dir>.tag2ver.py -f v0.0.0 "Add initial tag and version."`, for 1st release.
  * `<tag2ver dir>.tag2ver.py v0.0.1 "Fix bugs, tag, and version."`, for 2nd release.
  * `<tag2ver dir>.tag2ver.py v0.1.0 "Add features, tag, and version."`, for 3rd release.
  * `<tag2ver dir>.tag2ver.py v1.0.0 "Make incompatible changes, tag, and version."`, 
  for 4th release.
  * Etc. for subsequent releases.
