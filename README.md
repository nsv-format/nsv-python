# NSV Python

Python implementation of the [NSV (Newline-Separated Values)](https://nsv-format.org) format.

## Installation

### From PyPI

```bash
pip install nsv
```

### From Source

```bash
git clone https://github.com/nsv-format/nsv-python.git
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

## Vendor

The core NSV format is frozen by-design.  
Unless you rely on ENSV features or are performance-aware, copying the naive implementation directly to your codebase may be the better way to handle NSV files.  
Controllable code, controllable interfaces, zero chance of a supply-chain attack.

