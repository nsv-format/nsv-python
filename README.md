# NSV Python

Python implementation of the [NSV (Newline-Separated Values)](https://github.com/namingbe/nsv) format.

## Installation

### From PyPI

```bash
pip install nsv
```

### From Source

```bash
git clone https://github.com/namingbe/nsv-python.git
cd nsv-python
pip install -e .
```

## Usage

### Basic Reading and Writing

```python
import nsv

with open('input.nsv', 'r') as f:
    # load/dump are non-resumable
    reader = nsv.load(f)
    for row in reader:
        print(row)

with open('output.nsv', 'w') as f:
    # Reader/Writer are resumable, intended for streaming
    writer = nsv.Writer(f)
    writer.write_row(['row1cell1', 'row1cell2', 'row1cell3'])
    writer.write_row(['row2cell1', 'row2cell2', 'row2cell3'])
```

### Running Tests

**Important**: Always run tests from the project root to test local code changes (not the installed package):

```bash
python -m unittest discover -s tests -p 'test*.py' -v
```

Alternatively, install in editable mode:

```bash
pip install -e .
```

## Features

- [x] Core parsing
- [x] Resumable consumption
- [x] `spill`/`unspill` operations
- [ ] Integrate `nsv-rust` to performance

