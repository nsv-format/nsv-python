from setuptools import setup, find_packages

try:
    from setuptools_rust import Binding, RustExtension
    rust_extensions = [RustExtension("nsv._rust", path="rust/Cargo.toml", binding=Binding.PyO3, optional=True)]
except ImportError:
    rust_extensions = []

setup(
    name="nsv",
    version="0.2.2",
    packages=find_packages(),
    description="Python implementation of the NSV (Newline-Separated Values) format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="naming",
    author_email="",
    url="https://github.com/namingbe/nsv-python",
    project_urls={
        "Bug Reports": "https://github.com/namingbe/nsv-python/issues",
        "Source": "https://github.com/namingbe/nsv-python",
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
        "Operating System :: OS Independent",
    ],
    keywords="nsv csv data format parser",
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "pandas": ["pandas"],
    },
    rust_extensions=rust_extensions,
    setup_requires=["setuptools-rust>=1.0"] if rust_extensions else [],
    zip_safe=False,
)
