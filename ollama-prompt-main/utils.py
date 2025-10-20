import os
import json
from dotenv import load_dotenv
import logging
import statistics
from collections import Counter

"""
Utility functions used across the project, including:
    - loading environment variables
    - file I/O
"""

def get_logger():
    """
    Get the logger.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger

def load_env(logger: logging.Logger=None):
    """
    Load the environment variables.
    """
    load_dotenv()
    vars = {
        "DATA_PATH": os.environ.get("DATA_PATH"),
        "CURRENT_ITERATION": os.environ.get("CURRENT_ITERATION"),
    }

    if logger:
        logger.info("Loaded environment variables")

    return vars

def save_file(
        data: dict, file_path: str,
        file_name: str, indent: int=4,
        logger: logging.Logger=None
):
    """
    Save the data json file.
    """
    # create the directory if it doesn't exist.
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
        if logger:
            logger.info(f"Created directory: {file_path}")
    
    # save the data to the json file.
    json_path = os.path.join(file_path, file_name)
    try:
        with open(json_path, "w") as f:
            if indent is None:
                json.dump(data, f)
            else:
                json.dump(data, f, indent=indent)

        if logger: logger.info(f"Saved data to: {file_path}")

    except Exception as e:
        if logger: logger.error(f"Error saving data to {json_path}: {e}")


def load_file(file_path, logger=None):
    """
    Load the data from a file.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        if logger: logger.info(f"Loaded data from: {file_path}")
        

    except FileNotFoundError:
        if logger: logger.error(f"File not found: {file_path}")
        return None

    return data


def annotate_with_self_consistency(self, doc_prompt: str, n_samples: int = 5):
    """
    Run multiple samples with different seeds / temperatures
    and return the majority-voted label.
    """
    results = []
    scores = []
    reasonings = []

    base_temp = self.config.temperature or 0.7
    base_seed = self.config.seed or 42

    for i in range(n_samples):
        # Slightly vary temperature and seed for diversity
        temp = base_temp + (0.05 * i)
        seed = base_seed + i

        # temporarily override client options
        self.ollama_client.options["temperature"] = temp
        self.ollama_client.options["seed"] = seed

        result = self.ollama_client.chat(doc_prompt)
        if result and "label" in result:
            results.append(result["label"].strip().lower())
            scores.append(result.get("score", None))
            reasonings.append(result.get("reasoning", ""))
    
    if not results:
        return None

    # Majority vote
    final_label = Counter(results).most_common(1)[0][0]

    # Optional average score (if provided)
    avg_score = statistics.mean([s for s in scores if s is not None]) if any(scores) else None

    return {
        "final_label": final_label,
        "votes": results,
        "avg_score": avg_score,
        "reasonings": reasonings
    }