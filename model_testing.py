import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from datasets import Dataset
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from transformers.training_args import TrainingArguments
from transformers import Trainer
import transformers
import torch
from sklearn.metrics import cohen_kappa_score
from transformers import (
    RobertaForSequenceClassification,
    RobertaTokenizerFast,
    DataCollatorWithPadding,
    DebertaV2Tokenizer,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from transformers import EarlyStoppingCallback
from scipy.special import softmax
from sklearn.metrics import log_loss
from scipy.optimize import minimize_scalar
from transformers import default_data_collator, AutoModelForMaskedLM
from datasets import concatenate_datasets
from torch.utils.data import WeightedRandomSampler
from collections import Counter
from transformers import DebertaV2ForSequenceClassification
from datasets import Value


if __name__ == "__main__":

    # Read in gold dataset (TEST SET)
    df_test = pd.read_excel("./final_data/gold_labels_100.xlsx")

    # Rename the columns to match training set
    df_test = df_test.rename(columns={"Text": "text", "IsOthering": "label"})

    # Yes = 1, No = 0
    df_test["label"] = df_test["label"].map({"No": 0, "Yes": 1})

    # Read in noisy dataset (TRAIN SET)
    data_path = "./final_data/15k_annotated.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to DataFrame
    df_train = pd.DataFrame.from_dict(data, orient="index")

    # Extract labels from annotations
    df_train["label"] = df_train["annotation"].apply(
        lambda x: x.get("label") if isinstance(x, dict) else None
    )

    # None = 0, Othering = 1
    label_map = {"None": 0, "Othering": 1}
    df_train["label"] = df_train["label"].map(label_map)

    df_train["text"] = df_train["text"].astype(str)
    df_train = df_train.dropna(subset=["label", "text"]).reset_index(drop=True)

    df_train_split, df_val_split = train_test_split(
        df_train, test_size=0.1, random_state=42
    )

    train_dataset = Dataset.from_pandas(df_train_split[["text", "label"]])
    test_dataset = Dataset.from_pandas(df_test[["text", "label"]])
    val_dataset = Dataset.from_pandas(df_val_split[["text", "label"]])

    def compute_metrics(p):
        preds = p.predictions.argmax(-1)
        labels = p.label_ids
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, preds, average="binary"
        )
        acc = accuracy_score(labels, preds)
        kappa = cohen_kappa_score(labels, preds)

        return {
            "accuracy": acc,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "kappa": kappa,
        }

    model_names = [
        "microsoft/deberta-v3-base",
        "microsoft/deberta-v3-large",
        "xlm-roberta-large",
        "facebook/roberta-hate-speech-dynabench-r4-target",
        "vinai/bertweet-large",
    ]

    results = {}

    for model_path in model_names:
        print(f"\n=== Training {model_path} ===")

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_path, use_safetensors=True
        )

        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=200,  # adjust if you have longer comments
                padding="max_length",
            )

        tokenized_train = train_dataset.map(tokenize_function, batched=True)
        tokenized_val = val_dataset.map(tokenize_function, batched=True)
        tokenized_test = test_dataset.map(tokenize_function, batched=True)

        def format_dataset(ds):
            if "text" in ds.column_names:
                ds = ds.remove_columns(["text"])
            if "label" in ds.column_names:
                ds = ds.rename_column("label", "labels")
            ds = ds.cast_column("labels", Value("int64"))
            return ds

        tokenized_train = format_dataset(tokenized_train)
        tokenized_val = format_dataset(tokenized_val)
        tokenized_test = format_dataset(tokenized_test)

        for ds_name, ds in [
            ("train", tokenized_train),
            ("val", tokenized_val),
            ("test", tokenized_test),
        ]:
            if "__index_level_0__" in ds.column_names:
                ds = ds.remove_columns("__index_level_0__")
            print(f"{ds_name} columns →", ds.column_names)

            # reassign cleaned version
            if ds_name == "train":
                tokenized_train = ds
            elif ds_name == "val":
                tokenized_val = ds
            else:
                tokenized_test = ds

        batch = tokenized_train[0]

        with open("./final_data/anchor_dataset.json", "r", encoding="utf-8") as f:
            anchor_data = json.load(f)

        anchor_df = pd.DataFrame.from_dict(anchor_data, orient="index")
        anchor_df["label"] = anchor_df["annotation"].apply(lambda x: int(x["label"]))
        anchor_df = anchor_df[["text", "label"]]  # drop annotation
        anchor_df_oversampled = pd.concat([anchor_df] * 20, ignore_index=True)

        anchor_dataset = Dataset.from_pandas(anchor_df_oversampled[["text", "label"]])
        tokenized_anchor = anchor_dataset.map(tokenize_function, batched=True)
        tokenized_anchor = tokenized_anchor.rename_column("label", "labels")
        tokenized_anchor = tokenized_anchor.remove_columns(["text"])

        new_train_dataset_tokenized = concatenate_datasets(
            [tokenized_train, tokenized_anchor]
        )

        data_collator = DataCollatorWithPadding(tokenizer)

        training_args = TrainingArguments(
            output_dir=f"./results/{model_path.replace('/', '_')}/",
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=1,
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_ratio=0.1,
            logging_steps=50,
            save_strategy="epoch",
            eval_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=new_train_dataset_tokenized,
            tokenizer=tokenizer,
            eval_dataset=tokenized_val,
            compute_metrics=compute_metrics,
            data_collator=data_collator,
        )

        trainer.train()
        eval_result = trainer.evaluate()
        results[model_path] = eval_result
        print(eval_result)
