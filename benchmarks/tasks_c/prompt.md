# Task C — Write Data into a Text File

Write a Python function that writes a string of data into a text file.

## Requirements
- The function must accept a file path and a string of content as parameters.
- The function must write the content to the specified file, creating it if it does not exist.
- The function must use proper file handling (e.g. `with` statement).
- The function must handle errors that may occur during the write operation (e.g. permission errors, invalid path).
- The function must return `True` if the write was successful, `False` otherwise.

## Function signature
```python
def write_text_file(file_path: str, content: str) -> bool:
    ...
```
