import pandas as pd
from tqdm import tqdm
import json
import re
import numpy as np
import random

sheet_id = "1ANErBpHQAW6ngn1kq-a7rPpeTosG-z2PHnwfUT6IUKI"

OUTPUT_FILEPATH = "dataset_variable_filter.json"

SHEETS_TO_PROCESS = list(range(8, 27))

print("Starting conversion...")


# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={sheet_id}&format=xlsx"
)

variables_dict = {}

# let's process each sheet

for index, sheet_number in enumerate(tqdm(SHEETS_TO_PROCESS)):
    # read each sheet
    dataframe = pd.read_excel(xls, sheet_name=sheet_number)

    for (
        vname,
        terms,
        entity,
        description,
        object_property,
        datatype,
        dataset,
        dataelementconcept,
    ) in dataframe[
        [
            "ObjectPropertyLabelEN",
            "Vocabulary",
            "ObjectClass",
            "DataElementConceptDefEN",
            "ObjectProperty",
            "FormatConceptualDomain",
            "Dataset",
            "DataElementConcept",
        ]
    ].itertuples(
        index=False
    ):
        if dataset == "H&N\nSarc.":
            dataset = "both"
        # if dataset contains both H&N and Sarc, we will set it to both
        elif "H&N" in dataset and "Sarc." in dataset:
            dataset = "both"
        elif dataset == "H&N":
            dataset = "head_and_neck"
        elif dataset == "Sarc.":
            dataset = "sarcoma"
        else:
            dataset = "other"
        variables_dict[dataelementconcept] = dataset


# Serializing json
json_object = json.dumps(variables_dict, indent=4)

# Writing to sample.json
with open(OUTPUT_FILEPATH, "w") as outfile:
    outfile.write(json_object)
