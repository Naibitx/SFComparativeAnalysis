import os


def create_workspace(run_id, task_code, assistant):
    #this will create the file folder structure:
    #workspace/run_id/task_x/assistant/

    path = f"workspace/{run_id}/task_{task_code}/{assistant}"
    os.makedirs(path, exist_ok=True)
    return path


def save_file(folder, filename, content):#save the content into a file

    file_path = os.path.join(folder, filename)

    with open(file_path, "w") as f:
        f.write(content)

    return file_path