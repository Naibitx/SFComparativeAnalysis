# Comparative Analysis of AI Coding Assistants

## Overview

This project presents a full-stack framework for evaluating and comparing multiple AI coding assistants across standardized programming tasks. The system automates the process of generating code, executing it in a controlled environment, and measuring performance using consistent evaluation metrics.

The goal of this project is to provide a structured, data-driven approach to assess the reliability, correctness, efficiency, and security of AI-generated code.

---

## Features

- Integration of multiple AI coding assistants:
  - ChatGPT
  - Google Gemini
  - Anthropic Claude
  - Grok
  - GitHub Copilot

- Automated evaluation pipeline:
  - Prompt generation
  - Code generation via APIs
  - Execution in a sandboxed environment
  - Metric computation
  - Result storage and visualization

- Evaluation metrics:
  - Compilation success
  - Runtime correctness
  - Execution time (milliseconds)
  - Memory usage (megabytes)
  - Security vulnerabilities
  - Readability score

- Backend built with FastAPI and SQLAlchemy

- Frontend dashboard built with React (Vite)

- SQLite database for persistent storage

---

## Benchmark Tasks

The system evaluates assistants using the following standardized tasks:

- Task A: Read text file  
- Task B: Read JSON using multithreading  
- Task C: Write to a text file  
- Task D: Write JSON using multithreading  
- Task E: Create a ZIP file  
- Task F: Connect to and query a MySQL database  
- Task G: Connect to and query a MongoDB database  
- Task H: Implement a basic authentication system  

Each task includes predefined prompts, expected behaviors, and evaluation conditions.

---

## System Architecture

The system consists of three main components:

1. Backend (FastAPI)
   - Handles API requests
   - Integrates AI assistants
   - Executes generated code
   - Computes evaluation metrics
   - Stores results in the database

2. Frontend (React)
   - Provides a user interface for running tasks
   - Displays comparison tables and reports
   - Visualizes assistant performance

3. Database (SQLite)
   - Stores evaluation runs
   - Tracks assistant performance metrics
   - Maintains task and result history

---
