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

final_json = {
    "variables": {},
    "centers": {},
    "cancer_types": {"head_and_neck": "ct_1", "sarcoma": "ct_2"},
}

for i, center in enumerate(CENTERS):
    final_json["centers"][center] = "center_" + str(i)

# let's process each sheet
n = 0
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
        identifier,
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
        values = []
        datasets = str(dataset).splitlines()

        for line in str(terms).splitlines():
            # Regular expression to match the format
            pattern = r"^(?P<text>[^-]+) - (?P<number>\d+)$"

            # Match the pattern
            match = re.match(pattern, line)
            # Check if the match was successful

            if match:
                text = match.group(
                    "text"
                ).strip()  # Extract and strip any leading/trailing whitespace
                values.append(text)
                # Convert the number to an integer
                # number = int(match.group("number"))
                # result_dict[text] = number  # Add to dictionary
                # key = entity + "_" + object_property + "_" + text
                # id_variable_term[key] = {
                #     "variable_name": vname,
                #     "term": text,
                #     "entity": entity,
                #     "description": description,
                #     "code": number,
                # }

        if entity == "HistologySubGroup":
            entity = "Diagnosis"
            vname = "Histology"
        if entity == "Subsite":
            entity = "Diagnosis"
            vname = "Topography"

        entity = re.sub(r"(?<!^)(?=[A-Z])", " ", entity).upper()

        if pd.isna(vname):
            vname = ""
        if pd.isna(description):
            description = ""
        if pd.isna(datatype):
            datatype = ""

        if datatype == "Code" or datatype == "CustomCode":
            datatype = "Label"
        if datatype == "Integer":
            datatype = "Number"

        centers = []
        for center in CENTERS:
            center_data = {
                "availability_d": random.choice([True, False]),
                "availability_p": random.choice([True, False]),
                "availability_r": random.choice([True, False]),
                "years": "2019-2021",
                "datasource_name": "National Registry",
                "datasource_information": "lorem ipsum",
                "n_cases": random.randint(10, 1000),
                "m_cases": random.randint(0, 100),
                "plausability_score": random.choice(
                    ["Does not apply", random.randint(0, 100)]
                ),
                "overall_score": random.choice(
                    ["Does not apply", random.randint(0, 100)]
                ),
            }
            centers.append({center: center_data})

        variable_json = {
            "variable_name": vname,
            "variable_description": description,
            "datatype": datatype,
            "entity": entity,
            "values": values,
            "dataset": datasets,
            "id": "v_" + str(n),
            # "centers": centers,
        }
        n += 1
        final_json["variables"][identifier] = variable_json


# Serializing json
json_object = json.dumps(final_json, indent=4)

# Writing to sample.json
with open("governance_metadata.json", "w") as outfile:
    outfile.write(json_object)
