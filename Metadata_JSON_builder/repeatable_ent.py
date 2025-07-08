import pandas as pd
from tqdm import tqdm
import json
import re
import numpy as np
import random

sheet_id = "1ANErBpHQAW6ngn1kq-a7rPpeTosG-z2PHnwfUT6IUKI"

OUTPUT_FILEPATH = "rep_entities.json"

SHEETS_TO_PROCESS = list(range(8, 27))
SHEETLIST = []

print("Starting conversion...")

final_json = {"non_repeteable_entities": {}, "repeatable_entities": {}}
entities_map = {"Patient": "non_repeteable_entities",
                        "PatientFollowUp": "repeatable_entities",
                        "HospitalData": "non_repeteable_entities",
                        "HospitalPatientRecords": "repeatable_entities",
                        "CancerEpisode": "repeatable_entities",
                        "Diagnosis": "repeatable_entities",
                 }  

# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={sheet_id}&format=xlsx"
)

variables_list = []

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

        # check if final json already has this entity
        if entity not in final_json:
            final_json[entity] = []

        final_json[entity].append(object_property)


# Serializing json
json_object = json.dumps(final_json, indent=4)

# Writing to sample.json
with open(OUTPUT_FILEPATH, "w") as outfile:
    outfile.write(json_object)
