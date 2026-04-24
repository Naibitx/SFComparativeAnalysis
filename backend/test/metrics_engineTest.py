from app.services.metrics_engine import MetricsEngine, TestCase
from app.integrations.chatgpt_integration import ChatGPTAssistant

assistant = ChatGPTAssistant(api_key="your_key", model_version="gpt-4o")

engine = MetricsEngine()

tests = [
    TestCase(input_data=2, expected_output=4, description="double 2"),
    TestCase(input_data=5, expected_output=10, description="double 5"),
]

result = engine.evaluate_assistant(
    assistant=assistant,
    prompt="Write a Python function named double_number(x) that returns x * 2",
    language="python",
    entry_function="double_number",
    test_cases=tests,
)

print(result)