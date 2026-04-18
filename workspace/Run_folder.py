import os
from datetime import datetime

class WorkspaceManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def create_run_folder(self, prefix="run"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{prefix}_{timestamp}"
        path = os.path.join(self.base_dir, folder_name)
        os.makedirs(path, exist_ok=True)
        return path
