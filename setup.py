import setuptools

import tag2ver


def read_text(file_name: str) -> str:
    with open(file_name, "r") as fh:
        return fh.read()


setuptools.setup(
    name="tag2ver",
    version="1.3.3",
    url=tag2ver.__repository__,
    license="MIT License",  # Can only have one line `license`; setuptools bug.
    author=tag2ver.__author__,
    author_email="howard.lovatt@gmail.com",
    description=tag2ver.HELP_TEXT,
    long_description=read_text("README.rst"),
    long_description_content_type="text/x-rst",
    py_modules=["tag2ver"],
    platforms=["any"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
