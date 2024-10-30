import pandas as pd
from tqdm import tqdm
import random

sheet_id = "1Vw1Dr2K4oG__cDQTutGaJhZvGUvQTLwc4qWreP6qMSs"

INPUT_FILEPATH = "IDEA4RC_DM_V1.xlsx"
OUTPUT_FILEPATH = "output.wsd"

START_STRING = """@startuml

<style>
title {
  HorizontalAlignment right
  FontSize 24
  FontColor blue
}

header {
  HorizontalAlignment center
  FontSize 18
  ' FontColor purple
}

footer {
  HorizontalAlignment left
  FontSize 28
  FontColor red
}

legend {
  FontSize 15
  BackGroundColor yellow
  Margin 10
  Padding 5
}

caption {
  FontSize 32
}

arrow {
  FontSize 18
  Padding 50
  Margin 50
}

</style>

header Draft

title IDEA4RC DataModel

' hide the spot
hide circle

' avoid problems with angled crows feet
skinparam linetype ortho\n"""

LEGEND_STRING = """legend
Text color:
Blue -> H&N, Sarc. 
Red -> H&N
Green -> Sarc.
---------
Shapes:
red -> Mandatory
yellow -> Recommended
green -> Optional
---------
Each variable (and entity if needed) is related to the datamodels,
HN means Head and Neck
S means Sarcoma
end legend"""

RELATION_STRING = """p "1" ||--|{ "1..N" hpr
hd "1" ||--|{ "1..N" hpr

p "1" ||--o{ "0..N" ce
p "1" ||--o{ "0..N" pfu

ce "1" ||--|{ "1..N" ee

ee "1" ||--o| "0..1" hs
ee "1" ||--o| "0..1" ss

st "1" ||--|{ "0..N" dft
ilp "1" ||--|{ "0..N" dft
olt "1" ||--|{ "0..N" dft

ee "1" ||--o{ "0..N" r
ee "1" ||--o{ "0..N" su
ee "1" ||--o{ "0..N" st
ee "1" ||--o{ "0..N" olt
ee "1" ||--o{ "0..N" ilp
ee "1" ||--o{ "0..N" gte
ee "1" ||--o{ "0..N" tr
ee "1" ||--o{ "0..N" pri


note as N1
The relations to AdverseEvent are a XOR
end note

su "1" ||--o{ "0..N" ae
'note on link: XOR
st "0..N" ||--o{ "1" ae
'note on link: XOR
r "1" ||--o{ "0..N" ae
'note on link: XOR

s .. N1
st .. N1
r .. N1"""

SHEETS_TO_PROCESS = list(range(5, 23))


def check_dataset(dataset):
    datasets = str(dataset).split()
    if len(datasets) == 2:
        return "blue"
    elif datasets[0] == "H&N":
        return "red"
    elif datasets[0] == "Sarc.":
        return "green"
    else:
        return "black"


def check_required(required):
    if required == "M":
        return "+"
    elif required == "R":
        return "#"
    elif required == "O":
        return "-"
    else:
        return "-"


def list_variable(variables, required, dataset):
    STRING = f""""""
    for i, variable in enumerate(variables):
        if pd.isna(variable): # na are grouping variables, we need to ignore them
            continue
        STRING = (
            STRING
            + f"{check_required(required[i])} <color:{check_dataset(dataset[i])}>{variable}</color>\n"
        )
    return STRING

#PK | {"TBD"}
#    --
def create_entity_string(title, short_name, variables, required, dataset):
    STRING = f"""object \"{title}\" as {short_name.lower() if title != "Surgery" else "su"} {{
    {list_variable(variables, required, dataset)}
    }}"""
    return STRING


print("Starting conversion...")

# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={sheet_id}&format=xlsx"
)

# let's process each sheet
with open(OUTPUT_FILEPATH, "w") as f:
    f.write(START_STRING)
    f.write("\n")
    for index, sheet_number in enumerate(tqdm(SHEETS_TO_PROCESS)):
        # read each sheet
        dataframe = pd.read_excel(xls, sheet_name=sheet_number)

        # required to min/max
        dataframe["min"] = [
            0 if dataframe.loc[:, "Required"][i] != "M" else 1
            for i in range(dataframe.shape[0])
        ]
        dataframe["max"] = [1 for _ in range(dataframe.shape[0])]

        f.write(
            create_entity_string(
                xls.sheet_names[sheet_number],
                "".join(
                    [char for char in xls.sheet_names[sheet_number] if char.isupper()]
                ),
                dataframe["ObjectProperty"],
                dataframe["Required"],
                dataframe["Dataset"],
            )
        )

        f.write("\n")
    f.write(RELATION_STRING)
    f.write("\n")
    f.write(LEGEND_STRING)
    f.write("\n")
    f.write("@enduml")
    f.close()
