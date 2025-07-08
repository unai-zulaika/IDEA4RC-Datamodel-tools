import pandas as pd
from tqdm import tqdm
import json
import re
import numpy as np
import random

sheet_id = "1ANErBpHQAW6ngn1kq-a7rPpeTosG-z2PHnwfUT6IUKI"

INPUT_FILEPATH = "IDEA4RC_DM_V1.xlsx"
OUTPUT_FILEPATH = "dm_metadata.json"

SHEETS_TO_PROCESS = list(range(8, 27))

CENTERS = [
    "INT",
    "ISS-FJD",
    "FPNS",
    "MSCI",
    "VGR",
    "MCCI",
    "UKE",
    "CLB",
    "APHP",
    "OUS",
    "MUH",
]

print("Starting conversion...")

# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={sheet_id}&format=xlsx"
)

variables_list = {}
entities = set()

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
        required,
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
            "Required",
        ]
    ].itertuples(
        index=False
    ):
        
        if entity == "HistologySubGroup":
            entity = "Diagnosis"
            vname = "Histology"
        if entity == "Subsite":
            entity = "Diagnosis"
            vname = "Topography"

        # entity = re.sub(r"(?<!^)(?=[A-Z])", " ", entity).upper()

        if pd.isna(vname):
            vname = ""
        if pd.isna(description):
            description = ""
        if pd.isna(datatype):
            datatype = ""
        if pd.isna(required):
            required = "O"

        variables_list[vname] = required
        entities.add(entity)


# Serializing json
json_object = json.dumps(variables_list, indent=4)

# Writing to sample.json
with open("variable_importance.json", "w") as outfile:
    outfile.write(json_object)

entities_json = {}
for entity in entities:
    entities_json[entity] = ""

with open("entities_cardinality.json", "w") as outfile:
    json.dump(entities_json, outfile, indent=4)
