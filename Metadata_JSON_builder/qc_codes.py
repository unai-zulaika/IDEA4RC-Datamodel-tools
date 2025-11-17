import pandas as pd
from tqdm import tqdm
import json
import re
import random

sheet_id = "1ANErBpHQAW6ngn1kq-a7rPpeTosG-z2PHnwfUT6IUKI"

INPUT_FILEPATH = "IDEA4RC_DM_V1.xlsx"
OUTPUT_FILEPATH = "id2codes.json"

SHEETS_TO_PROCESS = list(range(8, 27))

print("Starting conversion...")

# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={sheet_id}&format=xlsx"
)

codes_dict = {}

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
        if datatype == "Code" or datatype == "CustomCode":
            for line in str(terms).splitlines():
                # Skip empty or whitespace-only lines
                line = line.strip()
                if not line:
                    continue

                # Regular expression to match the format
                # Use .+ instead of [^-]+ to allow dashes in the text part (e.g., "Ex-drinker")
                pattern = r"^(?P<text>.+) - (?P<number>\d+)$"

                # Match the pattern
                match = re.match(pattern, line)

                print(match)
                if match:
                    text = match.group("text").strip()
                    number = int(match.group("number").strip())
                    key = vname + " - " + text
                    print(text, number)

                    if not dataelementconcept in codes_dict:
                        codes_dict[dataelementconcept] = []
                    if not number in codes_dict[dataelementconcept]:
                        codes_dict[dataelementconcept].append(number)
            # if dataelementconcept == "Patient_alcohol":
            #     print(codes_dict[dataelementconcept])
            #     exit()

# convert sets to lists
# for key in codes_dict:
#     codes_dict[key] = list(codes_dict[key])

# Serializing json
json_object = json.dumps(codes_dict, indent=4)

# Writing to sample.json
with open("codes_dictionary.json", "w") as outfile:
    outfile.write(json_object)
