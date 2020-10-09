import setuptools

import tag2ver


def read_text(file_name: str):
    with open(file_name, "r") as fh:
        return fh.read()


setuptools.setup(
    name='tag2ver',
    version='1.1.6',
    url=tag2ver.__repository__,
    license=read_text('LICENSE'),
    author=tag2ver.__author__,
    author_email='howard.lovatt@gmail.com',
    description='Easy release management: file versioning, git commit, git tagging, git remote, and PyPI.',
    # read_text('README.md') doesn't work because PyPi can't render README.md - PyPi bug.
    long_description=f'See <{tag2ver.__repository__}> for detailed description.',  # read_text('README.md'),
    long_description_content_type='text/markdown',
    py_modules=['tag2ver'],
    platforms=['any'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
