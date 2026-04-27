def build_prompt(task_code: str) -> str:
    task = task_code.lower()

    # Shared rules for ALL tasks
    base_rules = """
You are participating in a coding benchmark.

Rules:
- Return ONLY valid Python code
- Do NOT include explanations
- Do NOT include markdown (no ``` blocks)
- Do NOT use any AI APIs (OpenAI, Anthropic, Gemini, etc.)
- Code must be runnable as-is
"""

    # Task A — Read text file
    if task == "a":
        return base_rules + """
Task:
Read the contents of a text file.

Requirements:
- The file path MUST be stored in a variable named `file_path`
- Open the file in read mode
- Print the entire contents
- Do NOT hardcode file names
"""

    # 🔵 Task B — JSON + multithreading
    if task == "b":
        return base_rules + """
Task:
Read a JSON file using multithreading.

Requirements:
- Use a variable named `file_path`
- Use threading or concurrent.futures
- Load the JSON data
- Print values from at least one key
- Do NOT hardcode file name
"""

    # Task C — Write text file
    if task == "c":
        return base_rules + """
Task:
Write to a text file.

Requirements:
- Use a variable named `file_path`
- Write some sample text into the file
- Ensure the file is created successfully
"""

    # Task D — Write JSON
    if task == "d":
        return base_rules + """
Task:
Write a JSON file.

Requirements:
- Use a variable named `file_path`
- Create a dictionary with sample data
- Save it as JSON
"""

    # Task E — ZIP
    if task == "e":
        return base_rules + """
Task:
Create a ZIP file.

Requirements:
- Use Python standard library (zipfile)
- Compress an existing text file
- Save as output.zip
"""

    # Task F — MySQL (SIMULATED)
    if task == "f":
        return base_rules + """
Task:
Simulate connecting to a MySQL database.

Requirements:
- Write code that shows a connection structure
- Return a sample query result
- Do NOT actually connect to a real database
"""

    # Task G — MongoDB (SIMULATED)
    if task == "g":
        return base_rules + """
Task:
Simulate connecting to MongoDB.

Requirements:
- Show how data would be retrieved
- Return a sample document
- Do NOT use real database connections
"""

    # Task H — Authentication
    if task == "h":
        return base_rules + """
Task:
Create a simple authentication system.

Requirements:
- Use variables: correct_username and correct_password
- Use variables: input_username and input_password
- Compare them
- Print "Login successful" if correct
- Otherwise print "Login failed"
- Do NOT use external libraries
- Return only valid Python code
"""