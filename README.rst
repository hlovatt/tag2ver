``tag2ver``
===========

Easy release management: file versioning, git commit,
git tagging, and  optionally
Black, git remote, and PyPI. 

The name ``tag2ver`` is meant to convey that the utility
does everything from
git-tagging to file-versioning and all in between and
either side. In particular
``tag2ver``:

1. If ``Black``
   (https://black.readthedocs.io/en/stable/index.html)
   is installed,
   ``tag2ver`` will format all files with: ``black .``.

2. Updates ``py`` and ``pyi`` file's ``__version__``
   attribute with given incremented
   semantic-version (https://semver.org).

3. Updates ``version`` attribute of ``setup.py`` as above
   (if ``setup`` exists).

4. Git commits all modified files with given description.

5. Git tags git repository with given version.

6. Pushes to remote git (if remote exists).

7. Uploads to ``PyPI`` or ``Test PyPI`` with ``-t`` option
   (if ``setup.py`` exists).

``tag2ver`` is careful to check everything
before making changes,
i.e. it is heavily biased to finding and reporting
an error before attempting any actions.

The whole program is in the single file, ``tag2ver.py``,
(without any dependencies outside of Python itself) and
therefore ``tag2ver.py`` alone can be copied to
install the utility.

Alternatively::

  pip install --upgrade tag2ver

Before use with a remote git repository,
e.g. GitHub, you *must* cache your credentials
because you are not prompted.
See 
https://stackoverflow.com/questions/5343068/is-there-a-way-to-cache-https-credentials-for-pushing-commits
for how to cache credentials,
EG https://github.com/hickford/git-credential-oauth.
If you forget to cache credentials you will get a
128 error from the `git push` command.

Help Text
---------

Usage from *folder with git repository to tag and source
files to version*:

* ``python -m tag2ver [options] [<Major>.<Minor>.<Patch> "Release/commit Description."]``.

Options (order of options not important):

* ``-h`` or ``--help``, print short help message
  (rest of command line ignored).

* ``--version`` print version number of ``tag2ver``
  (rest of command line ignored).

* ``-f`` or ``--force``, force the given git (not PyPI)
  version even if it is not a single increment.

* ``-t`` or ``--test_pypi``, use ``Test PyPI`` instead
  of ``PyPI`` (if ``setup.py`` exists).
  Passes ``--repository testpypi`` onto twine
  (https://twine.readthedocs.io/en/latest/).

* ``-u <Username>`` or ``--username <Username>``,
  for ``PyPI``/``Test PyPI`` (if ``setup.py`` exists).
  Passed onto twine
  (https://twine.readthedocs.io/en/latest/).
  *Commonly* required with PyPI.

* ``-p <Password>`` or ``--password <Password>``,
  for ``PyPI``/``Test PyPI`` (if ``setup.py`` exists).
  Passed onto twine
  (https://twine.readthedocs.io/en/latest/).

Version in form ``<Major>.<Minor>.<Patch>``
(must be the 1st non-option):

* Must be a semantic version (https://semver.org)
  with format ``<Major>.<Minor>.<Patch>``,
  where ``Major``, ``Minor``, and ``Patch`` are positive
  integers or zero.

* Must be a single increment from previous git tag version,
  unless ``-f`` option given.

* If PyPI used must be at least one increment from PyPI
  version (``-f`` not considered for PyPI version comparison).

* Use:
  ``<tag2ver dir>.tag2ver.py -f 0.0.0
  "Add initial tag and version."``
  (or similar), for 1st tagging in the repository (note 1).

* Leading zeros are allowed but ignored, e.g. ``00.00.00``
  is the same as ``0.0.0``.

* Leading plus not allowed, e.g. ``+0.0.0`` is an error.

Note 1:

* Both ``py`` and ``pyi`` files still need version attr
  (though it can be an empty string),
  e.g. ``__version__ = ''``.

* Similarly ``setup``, e.g. ``version='0.0.0'``
  (must have a valid version though).

* Since ``setup`` must contain a valid version the
  smallest version that can be in PyPI is ``0.0.1``
  (since version in ``setup`` must be increased).
  In practice this isn't a
  problem since much development happens before ready for PyPI and therefore version
  already ``>0.0.0``.

Description usually in quotes (must be the 2nd non-option):

* Description of the version: a single, short, ideally
  < 50 characters, sentence with
  an imperative mood (in double quotes to allow spaces).

Actions ``tag2ver`` takes in order:

* Reformat all files with ``Black`` if ``Black`` installed.

* Checks git repository exists, if not exit.

* Checks version number is *a* single increment from last
  git tag (except ``-f`` option)
  and of form ``<Major>.<Minor>.<Patch>`` and description
  exists, if not exit.

* Checks if PyPI deployed (``setup.py`` must exist)
  (see note 2)

* Updates the ``__version__`` attribute of all the ``py``,
  except ``setup.py`` (see above),
  and ``pyi`` file's in the
  current directory and subdirectories with given version
  (``__version__`` attributes must already exist in all files).

* Commits all modified files, including ``py`` and ``pyi``
  files ``tag2ver`` has modified,
  with given description.

* Tags the repository with given version and given description.

* If ``remote`` repository exists, pushes ``origin`` to
  ``HEAD`` (typically ``main``).
  Remote git repositories require authentication typically
  using a credential helper,
  EG https://github.com/hickford/git-credential-oauth.

* If ``setup.py`` exists, uploads to ``PyPI``
  (or ``Test PyPI`` with ``-t`` option)
  with given version.
  Username, ``-u`` or ``--username``, and password,
  ``-p`` or ``--password``,
  may optionally be specified.
  To use an API token on PyPI or Test PyPI the username is
  ``__token__`` and the
  password is the relevant API token.
  (Upload uses Twine
  (https://twine.readthedocs.io/en/latest/);
  see link for other options for specifying username and
  password,
  EG ``keyring`` or ``~/.pypirc``.
  An example of a typical ``setup.py`` is ``tag2ver``'s
  ``setup.py``
  https://github.com/hlovatt/tag2ver/blob/main/setup.py.)

Note 2:

* Checks version number is at least one increment from
  last PyPI deployment
  (regardless of ``-f`` option - PyPI versioning cannot be
  overridden).

* Updates ``setup.py``'s ``version`` attribute with given
  version
  (``version`` kwarg must already exist).

* Checks that ``tag2ver`` is *not* running inside a virtual
  environment;
  see next point, ``pip`` is used with option ``--User``
  that is not supported
  inside virtual environments.

* From PyPI updates ``pip``, ``setuptools``, ``wheel``,
  ``twine``, and ``packaging``,
  using option ``--User`` so that the global versions
  for other users are not affected.

EG:

* ``python -m tag2ver -h`` prints help.

* ``python -m tag2ver -f 0.0.0 "Add initial tag and version."``
  for 1st release (note ``-f`` and note ``0.0.0`` cannot
  be pushed to PyPI).

* ``python -m tag2ver 0.0.1 "Fix bugs, tag, and version."``.

* ``python -m tag2ver 0.1.0 "Add features, tag, and version."``.

* ``python -m tag2ver 1.0.0 "Make incompatible changes, tag,
  and version."``.

* ``python -m tag2ver -u <PyPI user name> 1.0.1 "Push to PyPI."``.
  Might need password as well, depending on Twine
  (https://twine.readthedocs.io/en/latest/) setup, and
  requires ``setup.py``.
