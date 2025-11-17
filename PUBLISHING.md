# Publishing Guide

## Overview

Publishing to PyPI requires building wheels for all platform/Python combinations and uploading them together. Users will automatically get the right wheel for their system.

The package has **graceful fallback**: if no wheel matches the user's platform, pip installs from source and uses the Python implementation (slower but fully functional).

## Local Build Workflow (Recommended)

The package consists of:
1. **Rust extension** (`nsv_rust_ext`) - Built with maturin
2. **Python package** (`nsv`) - Pure Python, built with setuptools

### Build Rust Extension Wheels

```bash
# Install maturin
pip install maturin

cd rust-ext

# Build for all Python versions on current platform
maturin build --release -i python3.8 -i python3.9 -i python3.10 -i python3.11 -i python3.12

# For cross-platform builds using Docker (Linux host)
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build --release
```

For comprehensive multi-platform builds, use the maturin Docker images:
```bash
# Linux x86_64
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build --release

# Linux aarch64 (via QEMU)
docker run --rm -v $(pwd):/io --platform linux/arm64 ghcr.io/pyo3/maturin build --release

# macOS and Windows require building on those platforms or using cross-compilation
```

Wheels will be in `rust-ext/target/wheels/`

### Build Python Source Distribution

```bash
# From repository root
python setup.py sdist

# Source distribution in dist/
```

### Publish

```bash
pip install twine

# Upload both Rust extension wheels and Python source distribution
twine upload rust-ext/target/wheels/* dist/*.tar.gz
```

## What Gets Published

Example for version 0.0.2:
- `nsv-0.0.2-cp38-cp38-manylinux_2_17_x86_64.whl`
- `nsv-0.0.2-cp39-cp39-manylinux_2_17_x86_64.whl`
- `nsv-0.0.2-cp312-cp312-win_amd64.whl`
- `nsv-0.0.2-cp312-cp312-macosx_11_0_arm64.whl`
- ... (~15 wheels total, one per Python version per platform)
- `nsv-0.0.2.tar.gz` (source distribution)

When users run `pip install nsv`:
1. pip tries to find a matching wheel for their platform/Python version
2. If found: Installs wheel with Rust extension (fast)
3. If not found: Falls back to source distribution, uses Python implementation (slower but works everywhere)

## CI Workflow (When Quota Available)

The `.github/workflows/wheels.yml` workflow can also build wheels, but requires GitHub Actions quota. Trigger manually via GitHub UI, then download artifacts and publish with twine.
