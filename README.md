``tag2var``
===========

Easy release management: file versioning, git commit, git tagging, and  optionally 
git remote and PyPI. 

The name ``tag2var`` is meant to convey that the utility does everything from 
git-tagging to file-versioning and all in between and either side. In particular
``tag2var``:

  1. Updates ``py`` and ``pyi`` file's ``__version__`` attribute with given incremented 
     semantic-version (<https://semver.org>).

  2. Updates ``version`` attribute of ``setup.py`` as above (if ``setup`` exists).

  3. Git commits all modified files with given description.

  4. Git tags git repository with given version and given description.

  5. Pushes to remote git (if remote exists).

  6. Uploads to ``PyPI`` or ``Test PyPi`` with ``-t`` option (if ``setup.py`` exists).

The whole program is in the single file, ``tag2var.py``, (without any dependencies outside 
Python3.6+) and therefore this file alone can be copied to install the utility. 
Alternatively::

    pip3 install tag2ver

``tag2ver`` is careful to check everything before making changes, i.e. it is heavily
biased to finding and reporting an error before attempting any actions.

Help Text
---------

Usage from *folder with git repository to tag and source files to version*:

  *  ``tag2ver.py [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]`` 
     if ``tag2ver.py`` is executable and on execution path.

  *  ``<tag2ver dir>.tag2ver.py [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]`` 
     if ``tag2ver.py`` is executable but not on execution path.

  *  ``python3 <tag2ver dir>.tag2ver.py [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]``.

Options (order of options not important):

  * ``-h`` or ``--help``, print short help message (rest of command line ignored).

  * ``--version`` print version number of ``tag2ver`` (rest of command line ignored).

  * ``-f`` or ``--force``, force the given git (not PyPI) version even if it is not a single 
    increment.

  * ``-t`` or ``--test_pypi``, use ``Test PyPi`` instead of ``PyPi`` (if ``setup.py`` exists).
    (Passes ``--repository testpypi`` onto twine (<https://twine.readthedocs.io/en/latest/>).)

  * ``-u <Username>`` or ``--username <Username>``, for ``PyPi``/``Test PyPi`` (if ``setup.py`` exists).
    (Passed onto twine (<https://twine.readthedocs.io/en/latest/>).)

  * ``-p <Password>`` or ``--password <Password>``, for ``PyPi``/``Test PyPi`` (if ``setup.py`` exists).
    (Passed onto twine (<https://twine.readthedocs.io/en/latest/>).)

Version in form <Major>.<Minor>.<Patch> (must be the 1st non-option):

  * Must be a semantic version (<https://semver.org>) with format ``<Major>.<Minor>.<Patch>``,
    where ``Major``, ``Minor``, and ``Patch`` are positive integers or zero.

  * Must be a single increment from previous git tag version, unless ``-f`` option given.

  * If PyPi used must be at least one increment from PyPI version 
    (``-f`` not considered for PyPI version comparison).

  * Use: ``<tag2ver dir>.tag2ver.py -f 0.0.0 "Add initial tag and version."`` 
    (or similar), for 1st tagging in the repository (note 1)

  * Leading zeros are allowed but ignored, e.g. ``00.00.00`` is the same as ``0.0.0``.

  * Leading plus not allowed, e.g. ``+0.0.0`` is an error.

Note 1:

  * Both ``py`` and ``pyi`` files still need version attr (though it can be an empty string), 
    e.g. ``__version__ = ''``.

  * Similarly ``setup``, e.g. ``version='0.0.0'`` (must have a valid version though).

  * Since ``setup`` must contain a valid version the smallest version that can be in PyPi
    is ``0.0.1`` (since version in ``setup`` must be increased). In practice this isn't a 
    problem since much development happens before ready for PyPI and therefore version 
    already ``>0.0.0``.

Description usually in quotes (must be the 2nd non-option):

  * Description of the version: a single, short, ideally < 50 characters, sentence with 
    an imperative mood (in double quotes to allow spaces).

Actions ``tag2ver`` takes in order:

  * Checks git repository exists.

  * Checks version number is *a* single increment from last git tag (except ``-f`` option) 
    and of form ``<Major>.<Minor>.<Patch>`` and description exists.

  * Checks if PyPI deployed (``setup.py`` must exist) (see note 2)

  * Updates the ``__version__`` attribute of all the ``py``, except ``setup.py`` (see above), 
    and ``pyi`` file's in the 
    current directory and sub-directories with given version 
    (``__version__`` attributes must already exist in all files).

  * Commits all modified files, including ``py`` and ``pyi`` files ``tag2ver`` has modified, 
    with given description.

  * Tags the repository with given version and given description.

  * If ``remote`` repository exists, pushes ``origin`` to ``master``.

  * If ``setup.py`` exists, uploads to ``PyPI`` (or ``Test PyPi`` with ``-t`` option) with given 
    version. 
    Username, ``-u`` or ``--username``, and password, ``-p`` or ``--password``, 
    may optionally be specified.
    (Upload uses twine (<https://twine.readthedocs.io/en/latest/>), 
    see link for other options for specifying username and password.)

Note 2:

  * Checks version number is at least one increment from last PyPI deployment 
    (regardless of ``-f`` option - PyPi versioning cannot be overridden).

  * Updates ``setup.py``'s ``version`` attribute with given version 
    (``version`` kwarg must already exist).

EG:

  * ``<tag2ver dir>.tag2ver.py -h`` prints help.

  * ``<tag2ver dir>.tag2ver.py -f 0.0.0 "Add initial tag and version."`` 
    for 1st release (note ``-f`` and note ``0.0.0`` cannot be pushed to PyPI).

  * ``<tag2ver dir>.tag2ver.py 0.0.1 "Fix bugs, tag, and version."`` for 2nd release.

  * ``<tag2ver dir>.tag2ver.py 0.1.0 "Add features, tag, and version."`` for 3rd release.

  * ``<tag2ver dir>.tag2ver.py 1.0.0 "Make incompatible changes, tag, and version."`` 
    for 4th release.

  * Etc. for subsequent releases.
