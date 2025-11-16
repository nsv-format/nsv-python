use pyo3::prelude::*;
use pyo3::types::PyList;

/// Parse NSV string into a list of lists
#[pyfunction]
fn loads(py: Python, s: &str) -> PyResult<PyObject> {
    let data = nsv::loads(s);

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
    Ok(nsv::dumps(&data))
}

/// A Python module implemented in Rust.
#[pymodule]
fn nsv_rust_ext(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(loads, m)?)?;
    m.add_function(wrap_pyfunction!(dumps, m)?)?;
    Ok(())
}
