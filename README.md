Tag git repository with incremented [semantic version](https://semver.org) and description
and update `py` and `pyi` file's `__version__` attribute to semanic version and description.

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
