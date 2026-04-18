"""
Database seeding script for the SF Comparative Analysis application.
Populates the database with model definitions and standardized benchmark scores.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db_manager
from backend.models import EmbeddingModel, Dataset, BenchmarkRun
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Aligned with MODEL_SCORES and MODEL_PERFORMANCE registry
EMBEDDING_MODELS = [
    {
        "name": "ChatGPT",
        "provider": "OpenAI",
        "version": "GPT-4",
        "dimension": 1536,
        "max_input_tokens": 128000,
        "cost_per_million_tokens": 0.03,
        "description": "ChatGPT (GPT-4) model for high-fidelity code and reasoning"
    },
    {
        "name": "Claude",
        "provider": "Anthropic",
        "version": "3 Opus",
        "dimension": 1024,
        "max_input_tokens": 200000,
        "cost_per_million_tokens": 0.015,
        "description": "Anthropic's Claude 3 Opus for complex reasoning"
    },
    {
        "name": "Gemini Pro",
        "provider": "Google",
        "version": "1.0",
        "dimension": 768,
        "max_input_tokens": 32768,
        "cost_per_million_tokens": 0.000125,
        "description": "Google's Gemini Pro optimized for speed and context"
    },
    {
        "name": "Copilot",
        "provider": "Microsoft/Anthropic",
        "version": "3 Sonnet Tier",
        "dimension": 1024,
        "max_input_tokens": 200000,
        "cost_per_million_tokens": 0.003,
        "description": "Copilot implementation aligned with Claude 3 Sonnet tier"
    },
    {
        "name": "Grok",
        "provider": "xAI",
        "version": "1.0",
        "dimension": 1024,
        "max_input_tokens": 8192,
        "cost_per_million_tokens": 0.0,
        "description": "xAI's open-source model optimized for real-time throughput"
    },
]

# Standardized Datasets based on SRS requirements
DATASETS = [
    {"name": "MMLU-Pro", "domain": "knowledge", "size": 12000, "description": "Massive Multitask Language Understanding"},
    {"name": "GPQA Diamond", "domain": "reasoning", "size": 200, "description": "Expert-level reasoning tests"},
    {"name": "SWE-bench Verified", "domain": "software", "size": 500, "description": "Real-world software engineering"},
    {"name": "HumanEval", "domain": "code", "size": 164, "description": "Python code generation"},
]

# Standardized Benchmark Results based on MODEL_SCORES
BENCHMARK_RESULTS = [
    # ChatGPT (GPT-4) Scores
    {"benchmark_name": "MMLU-Pro", "model_name": "ChatGPT", "score": 92.0, "total_tests": 100, "passed_tests": 92},
    {"benchmark_name": "GPQA Diamond", "model_name": "ChatGPT", "score": 87.0, "total_tests": 100, "passed_tests": 87},
    {"benchmark_name": "SWE-bench Verified", "model_name": "ChatGPT", "score": 94.0, "total_tests": 100, "passed_tests": 94},
    {"benchmark_name": "HumanEval", "model_name": "ChatGPT", "score": 88.0, "total_tests": 100, "passed_tests": 88},
    
    # Claude (Opus) Scores
    {"benchmark_name": "MMLU-Pro", "model_name": "Claude", "score": 90.0, "total_tests": 100, "passed_tests": 90},
    {"benchmark_name": "GPQA Diamond", "model_name": "Claude", "score": 85.0, "total_tests": 100, "passed_tests": 85},
    {"benchmark_name": "SWE-bench Verified", "model_name": "Claude", "score": 92.0, "total_tests": 100, "passed_tests": 92},
    {"benchmark_name": "HumanEval", "model_name": "Claude", "score": 86.0, "total_tests": 100, "passed_tests": 86},

    # Gemini Pro Scores
    {"benchmark_name": "MMLU-Pro", "model_name": "Gemini Pro", "score": 85.0, "total_tests": 100, "passed_tests": 85},
    {"benchmark_name": "GPQA Diamond", "model_name": "Gemini Pro", "score": 79.0, "total_tests": 100, "passed_tests": 79},
    {"benchmark_name": "SWE-bench Verified", "model_name": "Gemini Pro", "score": 86.0, "total_tests": 100, "passed_tests": 86},
    {"benchmark_name": "HumanEval", "model_name": "Gemini Pro", "score": 80.0, "total_tests": 100, "passed_tests": 80},

    # Copilot (Sonnet) Scores
    {"benchmark_name": "MMLU-Pro", "model_name": "Copilot", "score": 79.0, "total_tests": 100, "passed_tests": 79},
    {"benchmark_name": "GPQA Diamond", "model_name": "Copilot", "score": 73.0, "total_tests": 100, "passed_tests": 73},
    {"benchmark_name": "SWE-bench Verified", "model_name": "Copilot", "score": 76.0, "total_tests": 100, "passed_tests": 76},
    {"benchmark_name": "HumanEval", "model_name": "Copilot", "score": 78.0, "total_tests": 100, "passed_tests": 78},

    # Grok Scores
    {"benchmark_name": "MMLU-Pro", "model_name": "Grok", "score": 75.0, "total_tests": 100, "passed_tests": 75},
    {"benchmark_name": "GPQA Diamond", "model_name": "Grok", "score": 70.0, "total_tests": 100, "passed_tests": 70},
    {"benchmark_name": "SWE-bench Verified", "model_name": "Grok", "score": 72.0, "total_tests": 100, "passed_tests": 72},
    {"benchmark_name": "HumanEval", "model_name": "Grok", "score": 75.0, "total_tests": 100, "passed_tests": 75},
]

# [Functions seed_embedding_models, seed_datasets, seed_benchmark_results, and main remain unchanged]
