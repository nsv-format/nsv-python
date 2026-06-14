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

# Note that on a file lacking cell/row boundaries
# at the end, load/loads will emit the incomplete row
with open('input.nsv', 'r') as f:
    data = nsv.load(f)  # -> List[List[str]]

with open('output.nsv', 'w') as f:
    nsv.dump(data, f)

# Reader/Writer are resumable
with (
    open('stream.nsv', 'r') as fr,
    open('stream.nsv', 'w', buffering=1) as fw,
):
    reader = nsv.Reader(fr)
    writer = nsv.Writer(fw)
    list(reader)  # []
    writer.write_row(['a', 'b', 'c'])
    list(reader)  # [['a', 'b', 'c']]
    fw.write('incomple')
    list(reader)  # []
    fw.write('te\nrow\n\n')
    list(reader)  # [['incomplete', 'row']]
    # don't reuse the same file-like object like that
    # outside of examples though
```

## Vendor

The core NSV format is frozen by-design.  
Unless you rely on ENSV features or are performance-aware, copying the naive implementation directly to your codebase may be the better way to handle NSV files.  
Controllable code, controllable interfaces, zero chance of a supply-chain attack.

