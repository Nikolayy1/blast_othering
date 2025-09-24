import json
import yaml
import os
import argparse

from utils import load_env, load_file, save_file
from ollama_utils import Annotate


"""
This script is used to generate annotations by an LLM 
for a given dataset using the Annotate class.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate a dataset using an LLM.")
    parser.add_argument(
        "--config",
        type=str,
        default="default.yaml",
        help="Name of config file in configs directory",
    )
    parser.add_argument(
        "--prompt_file_stage_1",
        type=str,
        help="The name of the json file in prompts/ to be used for stage 1.",
    )
    parser.add_argument(
        "--prompt_file_stage_2",
        type=str,
        help="The name of the json file in prompts/ to be used for stage 2.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Name of dataset to analyze in the 'DATA_DIR/' directory.",
    )
    parser.add_argument(
        "--out_filename",
        type=str,
        help="Name of the output file to save to in DATA_DIR/results.",
    )

    # LLM arguments for ollama.
    parser.add_argument(
        "--model",
        type=str,
        help="ollama model id of the LLM to use for the initial exploration.",
    )
    parser.add_argument(
        "--seed", type=int, help="The seed for the random number generator."
    )
    parser.add_argument(
        "--temperature", type=float, help="The temperature for sampling."
    )
    parser.add_argument(
        "--host", metavar="HOST", required=True, help="The host for the Ollama API."
    )
    parser.add_argument(
        "--port", metavar="PORT", required=True, help="The port for the Ollama API."
    )

    # Arguments for parallel processing and saving.
    parser.add_argument(
        "--workers", type=int, help="Number of workers to use for parallel processing."
    )
    parser.add_argument(
        "--save_interval", type=int, help="The interval at which to save the results."
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=5,
        help="Max # of tries for LLM to gen correctly formatted response.",
    )

    # load the environment variables.
    env_vars = load_env()
    DATA_PATH = env_vars["DATA_PATH"]
    CURRENT_ITERATION = env_vars["CURRENT_ITERATION"]
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    RESULT_PATH = os.path.join(DATA_PATH, "results", str(CURRENT_ITERATION))
    os.makedirs(RESULT_PATH, exist_ok=True)

    args = parser.parse_args()
    if args.config is not None:  # load the config file containing defaults.
        config_file = os.path.join(SCRIPT_PATH, "configs", args.config)
        config = yaml.safe_load(open(config_file)) if args.config is not None else {}
        parser.set_defaults(**config)
        args = parser.parse_args()

    if not args.out_filename:
        args.out_filename = f"stage_1_results_{CURRENT_ITERATION}.json"
    
    original_dataset = args.dataset

    # Stage 1
    annotator_stage_1 = Annotate(
        args,
        SCRIPT_PATH,
        DATA_PATH,
        RESULT_PATH,
        stage=1,
        curr_iteration=CURRENT_ITERATION,
    )
    annotator_stage_1.process_docs()

    # Load Stage 1 results
    stage_1_out_path = os.path.join(RESULT_PATH, args.out_filename)
    stage_1_results = load_file(stage_1_out_path)

    hate_only = {
        doc_id: {"text": doc["text"]}
        for doc_id, doc in stage_1_results["data"].items()
        if doc["annotation"] and doc["annotation"]["label"].lower() == "hate"
    }

    # Save filtered data for Stage 2
    stage2_dataset = f"stage_2_data_{CURRENT_ITERATION}.json"
    save_file(hate_only, RESULT_PATH, stage2_dataset)

    # Stage 2
    args.dataset = stage2_dataset
    args.out_filename = f"stage_2_results_{CURRENT_ITERATION}.json"

    annotator_stage_2 = Annotate(
        args, SCRIPT_PATH, os.path.join(DATA_PATH, f"results/{CURRENT_ITERATION}"), RESULT_PATH, stage=2, curr_iteration=CURRENT_ITERATION
    )
    annotator_stage_2.process_docs()
    

    # Load Stage 2 results
    stage_2_out_path = os.path.join(RESULT_PATH, args.out_filename)
    stage_2_results = load_file(stage_2_out_path)

    other_only = {
        doc_id: {"text": doc["text"]}
        for doc_id, doc in stage_2_results["data"].items()
        if doc["annotation"] and doc["annotation"]["label"].lower() == "other"
    }
    # Save filtered data for Stage 3
    stage3_dataset = f"stage_3_data_{CURRENT_ITERATION}.json"
    save_file(other_only, RESULT_PATH, stage3_dataset)
    
    # Stage 3
    args.dataset = stage3_dataset
    args.out_filename = f"stage_3_results_{CURRENT_ITERATION}.json"

    annotator_stage_3 = Annotate(
        args, SCRIPT_PATH, os.path.join(DATA_PATH, f"results/{CURRENT_ITERATION}"), RESULT_PATH, stage=3, curr_iteration=CURRENT_ITERATION
    )
    annotator_stage_3.process_docs()
    
    # Load Stage 2 results
    stage_2_out_path = os.path.join(RESULT_PATH, args.out_filename)
    stage_2_results = load_file(stage_2_out_path)

    other_only = {
        doc_id: {"text": doc["text"]}
        for doc_id, doc in stage_2_results["data"].items()
        if doc["annotation"] and doc["annotation"]["label"].lower() == "other"
    }
    # Save filtered data for Stage 4
    stage4_dataset = f"stage_4_data_{CURRENT_ITERATION}.json"
    save_file(other_only, RESULT_PATH, stage4_dataset)

    # Stage 4
    args.dataset = stage4_dataset
    args.out_filename = f"stage_4_results_{CURRENT_ITERATION}.json"

    annotator_stage_4 = Annotate(
        args, SCRIPT_PATH, os.path.join(DATA_PATH, f"results/{CURRENT_ITERATION}"), RESULT_PATH, stage=4, curr_iteration=CURRENT_ITERATION
    )
    annotator_stage_4.process_docs()

    # Load Stage 4 results
    stage_4_out_path = os.path.join(RESULT_PATH, args.out_filename)
    stage_4_results = load_file(stage_4_out_path)

    other_only = {
        doc_id: {"text": doc["text"]}
        for doc_id, doc in stage_4_results["data"].items()
        if doc["annotation"] and doc["annotation"]["label"].lower() == "other"
    }
    # Save filtered data for Stage 5
    stage5_dataset = f"stage_5_data_{CURRENT_ITERATION}.json"
    save_file(other_only, RESULT_PATH, stage5_dataset)
    
    # Stage 5
    args.dataset = stage5_dataset
    args.out_filename = f"stage_5_results_{CURRENT_ITERATION}.json"
    annotator_stage_5 = Annotate(
        args, SCRIPT_PATH, os.path.join(DATA_PATH, f"results/{CURRENT_ITERATION}"), RESULT_PATH, stage=5, curr_iteration=CURRENT_ITERATION
    )
    annotator_stage_5.process_docs()
    
    # Othering
    args.dataset = original_dataset
    args.out_filename = f"stage_6_results_{CURRENT_ITERATION}.json"

    annotator_othering = Annotate(
        args,
        SCRIPT_PATH,
        DATA_PATH,
        RESULT_PATH,
        stage=6,
        curr_iteration=CURRENT_ITERATION,
    )
    annotator_othering.process_docs()

