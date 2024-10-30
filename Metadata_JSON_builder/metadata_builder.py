import pandas as pd
from tqdm import tqdm
import json
import re
import numpy as np

sheet_id = "1Vw1Dr2K4oG__cDQTutGaJhZvGUvQTLwc4qWreP6qMSs"

INPUT_FILEPATH = "IDEA4RC_DM_V1.xlsx"
OUTPUT_FILEPATH = "dm_metadata.json"

SHEETS_TO_PROCESS = list(range(7, 24))

print("Starting conversion...")

# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={sheet_id}&format=xlsx"
)

variables_list = []

# let's process each sheet

for index, sheet_number in enumerate(tqdm(SHEETS_TO_PROCESS)):
    # read each sheet
    dataframe = pd.read_excel(xls, sheet_name=sheet_number)


    for vname, terms, entity, description, object_property, datatype, dataset in dataframe[
        ["ObjectPropertyLabelEN", "Vocabulary",
         "ObjectClass", "DataElementConceptDefEN", "ObjectProperty", "FormatConceptualDomain", "Dataset"]
    ].itertuples(index=False):
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

        variable_json = {
            "variable_name": vname,
            "variable_description": description,
            "datatype": datatype,
            "entity": entity,
            "values": values,
            "dataset": datasets
        }
        
        variables_list.append(variable_json)
            

# Serializing json
json_object = json.dumps(variables_list, indent=4)
 
# Writing to sample.json
with open("metadata.json", "w") as outfile:
    outfile.write(json_object)
