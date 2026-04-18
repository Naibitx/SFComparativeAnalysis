def build_prompt(task_code):
    #returns the standardized prompt for each task
    prompts = {
        "a": "Write code to read from a text file",
        "b": "Read JSON using threads",
        "c": "Write to text file",
        "d": "Write JSON with threads",
        "e": "Create zip file",
        "f": "Connect to MySQL",
        "g": "Connect to MongoDB",
        "h": "Authentication system",
    }
    return prompts.get(task_code, "Unknown task")