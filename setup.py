import setuptools


def read_text(file_name: str):
    with open(file_name, "r") as fh:
        return fh.read()


setuptools.setup(
    name='tag2ver-hlovatt',
    version='0.6.17',
    url='https://github.com/hlovatt/tag2ver',
    license=read_text('LICENSE'),
    author='Howard C Lovatt',
    author_email='howard.lovatt@gmail.com',
    description='Easy release management: file versioning, git commit, git tagging, git remote, and PyPI.',
    # read_text('README.md') doesn't work because PyPi can't render README.md - PyPi bug.
    long_description=read_text('README.md'), # 'See <https://github.com/hlovatt/tag2ver/README.md> for details.',  # read_text('README.md'),
    long_description_content_type='text/markdown',
    py_modules=['tag2ver'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
