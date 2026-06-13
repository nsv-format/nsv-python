import os

from setuptools import setup, find_packages

build_rust = os.environ.get("NSV_BUILD_RUST", "0") == "1"
if build_rust:
    from setuptools_rust import Binding, RustExtension
    rust_extensions = [RustExtension("nsv._rust", path="rust/Cargo.toml", binding=Binding.PyO3, optional=False)]
else:
    rust_extensions = []

setup(
    name="nsv",
    version="0.2.3",
    packages=find_packages(exclude=["tests", "tests.*"]),
    description="Python implementation of the NSV (Newline-Separated Values) format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="naming",
    author_email="",
    url="https://github.com/nsv-format/nsv-python",
    project_urls={
        "Bug Reports": "https://github.com/nsv-format/nsv-python/issues",
        "Source": "https://github.com/nsv-format/nsv-python",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    keywords="nsv csv data format parser",
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "pandas": ["pandas"],
    },
    rust_extensions=rust_extensions,
)
