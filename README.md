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

# Reading NSV data
with open('input.nsv', 'r') as f:
    reader = nsv.load(f)
    for row in reader:
        print(row)

# Writing NSV data
with open('output.nsv', 'w') as f:
    writer = nsv.Writer(f)
    writer.write_row(['row1cell1', 'row1cell2', 'row1cell3'])
    writer.write_row(['row2cell1', 'row2cell2', 'row2cell3'])
```

## Development

### Running Tests

**Important**: Always run tests from the project root to test local code changes (not the installed package):

```bash
python -m unittest discover -s tests -p 'test*.py' -v
```

Alternatively, install in editable mode:

```bash
pip install -e .
```

Must cover
- `loads(s)` vs `load(StringIO(s))` parity
- `dumps(data)` vs `dump(data, StringIO()).getvalue()` parity

## Features

- [x] Core parsing
- [ ] `table`

