"""
File utility functions used across the framework modules.
Handles reading, writing, and managing workspace artifacts.
"""

import os
import json
from datetime import datetime


def read_file(file_path: str) -> str:
    # reads and returns the content of any text file
    with open(file_path, "r") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    # writes content to a file, creating parent directories if needed
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)


def save_json(file_path: str, data: dict) -> None:
    # serializes and saves a dict as a JSON artifact (metrics, metadata, scan results)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(file_path: str) -> dict:
    # loads and returns a JSON artifact as a dict
    with open(file_path, "r") as f:
        return json.load(f)


def save_metadata(workspace: str, assistant: str, task: str, language: str, model_version: str = "") -> None:
    # saves assistant metadata alongside generated code 
    metadata = {
        "assistant":     assistant,
        "task":          task,
        "language":      language,
        "model_version": model_version,
        "timestamp":     datetime.utcnow().isoformat() + "Z",
    }
    save_json(os.path.join(workspace, "metadata.json"), metadata)


def file_exists(file_path: str) -> bool:
    return os.path.isfile(file_path)


def list_workspace_files(workspace: str) -> list[str]:
    # returns all file paths inside a workspace directory
    result = []
    for root, _, files in os.walk(workspace):
        for f in files:
            result.append(os.path.join(root, f))
    return result


def delete_workspace(workspace: str) -> None:
    # removes an entire workspace directory and its contents
    import shutil
    if os.path.exists(workspace):
        shutil.rmtree(workspace)