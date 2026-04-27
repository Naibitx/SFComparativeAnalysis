Write a Python function that reads data from a text file and returns its full contents as a string.

Requirements:
- The function must accept a file path as a parameter.
- The function must open and read the file using proper file handling (e.g. with statement).
- The function must return the file contents as a single string.
- The function must handle the case where the file does not exist.
- The function must close the file after reading.

Function signature:
def read_text_file(file_path: str) -> str:
    ...