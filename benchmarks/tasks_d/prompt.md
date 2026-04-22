# Task D — Write Data Values into a JSON File Using Multiple Threads

Write a Python function that writes data values into multiple JSON files concurrently using threads.

## Requirements
- The function must accept a list of `(file_path, data)` tuples as a parameter.
- The function must use Python's `threading` module to write each file in a separate thread.
- Each thread must independently serialize its data to JSON and write it to the assigned file path.
- The function must be thread-safe.
- The function must return a dictionary mapping each file path to `True` (write succeeded) or `False` (write failed).
- The function must handle write errors per thread without crashing the others.

## Function signature
```python
def write_json_files_threaded(file_data: list[tuple[str, any]]) -> dict[str, bool]:
    ...
```
