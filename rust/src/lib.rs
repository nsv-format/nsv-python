use pyo3::prelude::*;
use pyo3::types::PyList;

/// Parse NSV string into a list of lists of str
#[pyfunction]
fn loads<'py>(py: Python<'py>, s: &str) -> PyResult<Bound<'py, PyList>> {
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

    Ok(result)
}

/// Serialize data to NSV string
#[pyfunction]
fn dumps(data: Vec<Vec<String>>) -> PyResult<String> {
    Ok(nsv::encode(&data))
}

/// A Python module implemented in Rust.
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(loads, m)?)?;
    m.add_function(wrap_pyfunction!(dumps, m)?)?;
    Ok(())
}

