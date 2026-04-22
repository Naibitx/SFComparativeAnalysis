# Task E — Produce a Zip Archive via an External Application

Write a Python function that produces a zip archive by calling the system `zip` command as an external application, with an input text file supplied as an argument.

## Requirements
- The function must accept an input file path and an output zip file path as parameters.
- The function must use Python's `subprocess` module to invoke the external `zip` command.
- The function must not use Python's `zipfile` module — the zip must be produced by the external command.
- The function must return `True` if the archive was created successfully, `False` otherwise.
- The function must handle errors such as the `zip` command not being available or the input file not existing.

## Function signature
```python
def zip_file(input_path: str, output_zip_path: str) -> bool:
    ...
```
