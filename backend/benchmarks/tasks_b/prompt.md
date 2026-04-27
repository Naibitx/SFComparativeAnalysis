# Task B — Read Data Values from a JSON File Using Multiple Threads

Write a Python function that reads data values from multiple JSON files concurrently using threads.

## Requirements
- The function must accept a list of file paths as a parameter.
- The function must use Python's `threading` module to read each file in a separate thread.
- Each thread must read and parse one JSON file independently.
- The function must return a dictionary mapping each file path to its parsed JSON content.
- The function must be thread-safe when collecting results.
- The function must handle the case where a file does not exist or contains invalid JSON.

## Function signature
```python
def read_json_files_threaded(file_paths: list[str]) -> dict[str, any]:
    ...
```