def score_result(result: dict) -> float:

    execution = result.get("execution", {})
    metrics = result.get("metrics", {})
    score = 0

    if execution.get("success"):
        score += 50
    else:
        return 0#immediate failure, worst score

    if execution.get("stderr"):
        score -= 15
    exec_time = execution.get("execution_time", 10)
    #faster = higher score
    score += max(0, 20 - exec_time)

    if metrics.get("compile_success"):
        score += 10
    warnings = metrics.get("warnings", 0)
    score -= warnings * 2

    security_issues = metrics.get("security_issues", 0)
    score -= security_issues * 5
    return score

def rank_assistants(results: list) -> list:
    scored_results = []

    for result in results:
        assistant_name = result.get("assistant", "unknown")
        score = score_result(result)

        scored_results.append({
            "assistant": assistant_name,
            "score": round(score, 2)
        })

    #sort descending (highest score first)
    ranked = sorted(scored_results, key=lambda x: x["score"], reverse=True)

    return ranked


def get_best_assistant(results: list) -> dict:
    ranked = rank_assistants(results)
    if not ranked:
        return None

    return ranked[0]