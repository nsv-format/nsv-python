import os
import tempfile

import nsv

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')
SAMPLES_DATA = {
    'empty': [],
    'empty_one': [[]],
    'empty_two': [[], []],
    'empty_three': [[], [], []],
    'basic': [["a", "b", "c"], ["d", "e", "f"]],
    'comments': [["# This is a comment", "// Another comment", "-- And another"], ["---"], ["r1c1", "r1c2"], ["r2c1", "r2c2"]],
    'empty_fields': [["r1c1", "", "r1c3"], ["r2c1", "", "r2c3"]],
    'empty_sequence': [["r1c1", "r1c2"], [], ["r3c1", "r3c2"]],
    'empty_sequence_end': [["r1c1", "r1c2"], ["r2c1", "r2c2"], []],
    'empty_sequence_start': [[], ["r2c1", "r2c2"], ["r3c1", "r3c2"]],
    'special_chars': [
        ["field with spaces", "field,with,commas", "field\twith\ttabs"],
        ["field\"with\"quotes", "field'with'quotes", "field\\with\\backslashes"],
        ["field\nwith\nnewlines", "field, just field"],
    ],
    'multiple_empty_sequences': [
        [],
        ["r2c1", "r2c2"],
        [],
        [],
        ["r5c1", "r5c2", "r5c3"],
        [],
    ],
    'multiline_encoded': [["line1\nline2", "r1c2", "r1c3"], ["anotherline1\nline2\nline3", "r2c2"]],
    'escape_edge_cases': [
        ["\\n", "\\\n", "\\\\n"],
        ["\\\\", "\n\n"],
    ],
    'one_one': [['']],
}


def dump_then_load(data):
    return nsv.loads(nsv.dumps(data))


def load_then_dump(s):
    return nsv.dumps(*nsv.loads(s))


def load_sample(name):
    file_path = os.path.join(SAMPLES_DIR, f'{name}.nsv')
    with open(file_path, 'r') as f:
        data = nsv.load(f)
    return data


def loads_sample(name):
    file_path = os.path.join(SAMPLES_DIR, f'{name}.nsv')
    with open(file_path, 'r') as f:
        data = nsv.loads(f.read())
    return data


def dump_sample(name):
    data = SAMPLES_DATA[name]
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, f'output_{name}.nsv')
        with open(output_path, 'w') as f:
            nsv.dump(data, f)
        with open(output_path, 'r') as f:
            s = f.read()
    return s


def dumps_sample(name):
    return nsv.dumps(SAMPLES_DATA[name])
