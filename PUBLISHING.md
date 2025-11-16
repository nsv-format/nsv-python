# Publishing Guide

## Overview

Publishing to PyPI requires building wheels for all platform/Python combinations and uploading them together. Users will automatically get the right wheel for their system.

## Recommended Workflow: CI + Manual Upload

1. **Trigger the CI build** (via GitHub UI or push to master)
   - Builds wheels for: Linux (x86_64, aarch64), macOS (x86_64, aarch64), Windows (x64)
   - Tests on all platforms with Python 3.8-3.12
   - Cross-validates semantic compatibility

2. **Download artifacts from GitHub Actions**
   ```bash
   # Go to Actions tab -> latest workflow run -> download all wheel artifacts
   # Extract them into a local dist/ directory
   mkdir -p dist
   unzip wheels-linux-x86_64.zip -d dist/
   unzip wheels-linux-aarch64.zip -d dist/
   unzip wheels-macos-x86_64.zip -d dist/
   unzip wheels-macos-aarch64.zip -d dist/
   unzip wheels-windows-x64.zip -d dist/
   unzip sdist.zip -d dist/
   ```

3. **Publish to PyPI**
   ```bash
   pip install twine
   twine upload dist/*
   ```

You'll have ~10-15 wheel files (one per Python version per platform) plus the source distribution. All get uploaded in one command.

## Alternative: Fully Local Build

If you want to build everything locally without CI:

```bash
pip install maturin

# Build for your current platform only
cd rust-ext
maturin build --release -i python3.8 -i python3.9 -i python3.10 -i python3.11 -i python3.12

# Or use cibuildwheel for cross-platform (requires Docker)
pip install cibuildwheel
cibuildwheel --platform linux
```

Note: Local cross-platform builds are tedious. The CI workflow handles this better.

## What Gets Published

Example for version 0.0.2:
- `nsv-0.0.2-cp38-cp38-manylinux_2_17_x86_64.whl`
- `nsv-0.0.2-cp39-cp39-manylinux_2_17_x86_64.whl`
- `nsv-0.0.2-cp312-cp312-win_amd64.whl`
- `nsv-0.0.2-cp312-cp312-macosx_11_0_arm64.whl`
- ... (one per Python version per platform)
- `nsv-0.0.2.tar.gz` (source distribution for unsupported platforms)

When users run `pip install nsv`, pip selects the matching wheel automatically.
