use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList};

/// Parse NSV string into a list of lists of str
#[pyfunction]
fn loads(py: Python, s: &str) -> PyResult<PyObject> {
    let data = nsv::decode(s);

    // Convert Vec<Vec<String>> to Python list of lists
    let result = PyList::empty(py);
    for row in data {
        let py_row = PyList::empty(py);
        for cell in row {
            py_row.append(cell)?;
        }
        result.append(py_row)?;
    }

    Ok(result.into())
}

/// Serialize data to NSV string
#[pyfunction]
fn dumps(data: Vec<Vec<String>>) -> PyResult<String> {
    Ok(nsv::encode(&data))
}

/// Parse NSV bytes into a list of lists of bytes
#[pyfunction]
fn loads_bytes(py: Python, data: &[u8]) -> PyResult<PyObject> {
    let rows = nsv::decode_bytes(data);
    let result = PyList::empty(py);
    for row in rows {
        let py_row = PyList::empty(py);
        for cell in row {
            py_row.append(PyBytes::new(py, &cell))?;
        }
        result.append(py_row)?;
    }
    Ok(result.into())
}

/// Serialize a list of lists of bytes to NSV bytes.
///
/// Not part of the public API. Benchmarks show this is slower than dumps()
/// because PyO3 must copy every bytes cell into a Rust Vec<u8> before
/// encoding — same per-cell cost as the str path, plus extra indirection.
///
/// Prerequisites to make this worthwhile:
///   1. Caller already holds data as bytes (no str->bytes conversion upstream).
///   2. A streaming/writer API so the output doesn't need to be a single
///      allocated Python bytes object for the whole result.
///   3. Or: cells arrive pre-escaped so encoding reduces to assembly only.
#[pyfunction]
fn dumps_bytes(py: Python, data: Vec<Vec<Vec<u8>>>) -> PyResult<PyObject> {
    let result = nsv::encode_bytes(&data);
    Ok(PyBytes::new(py, &result).into())
}

/// A Python module implemented in Rust.
#[pymodule]
fn nsv_rust_ext(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(loads, m)?)?;
    m.add_function(wrap_pyfunction!(dumps, m)?)?;
    m.add_function(wrap_pyfunction!(loads_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(dumps_bytes, m)?)?;
    Ok(())
}
