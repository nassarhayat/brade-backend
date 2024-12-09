import json
import os
from agents.configs.agents import *
from agents.evals.eval_utils import run_function_evals

base_dir = os.path.dirname(__file__)
predictions = os.path.join(base_dir, "eval_cases/predictions.json")
predictions_evals = os.path.join(base_dir, "eval_results/predictions_evals.json")
n = 1

if __name__ == "__main__":
    
    # Run predictions evals
    with open(predictions, "r") as file:
        predictions = json.load(file)
    run_function_evals(
        general_agent,
        predictions,
        n,
        eval_path=predictions_evals,
    )