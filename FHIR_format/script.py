import pandas as pd
from tqdm import tqdm
import re

SHEET_ID = "1Vw1Dr2K4oG__cDQTutGaJhZvGUvQTLwc4qWreP6qMSs"

# INPUT_FILEPATH = 'IDEA4RC_DM_V1.xlsx'
OUTPUT_FILEPATH = "output_fhir.xlsx"

DROP_COLUMNS = [
    "Variable Name (EURACAN file)",
    "DataElementConcept",
    "ObjectClass",
    "ConventionEN",
    "Example",
    "Value in OMOP",
    "Notes",
]
COLUMNS_RENAME_MAP = {
    "ObjectProperty": "Element name",
    "ObjectPropertyLabelEN": "DataElement",
    "DataElementConceptDefEN": "Data element description",
    "FormatConceptualDomain": "dataType",
    "index": "Description",
}
COLUMNS_REORDER = [
    "Element name",
    "Dataset",
    "DataElement",
    "Data element description",
    "min",
    "max",
    "dataType",
    "Comment",
    "Codes",
]

SHEETS_TO_PROCESS = list(range(3, 19))

print("Starting conversion...")

# load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={SHEET_ID}&format=xlsx"
)

# let's process each sheet
with pd.ExcelWriter(OUTPUT_FILEPATH) as writer:
    for index, sheet_number in enumerate(tqdm(SHEETS_TO_PROCESS)):
        # read each sheet
        dataframe = pd.read_excel(xls, sheet_name=sheet_number)
        # drop undesired columns
        dataframe = dataframe.drop(columns=DROP_COLUMNS)

        # rename columns
        dataframe = dataframe.rename(columns=COLUMNS_RENAME_MAP)

        # clean empty rows
        dataframe = dataframe[dataframe["Element name"].notna()].reset_index()

        # required to min/max
        dataframe["min"] = [
            0 if dataframe.loc[:, "Required"][i] != "M" else 1
            for i in range(dataframe.shape[0])
        ]
        dataframe["max"] = [1 for _ in range(dataframe.shape[0])]
        dataframe = dataframe.drop(columns="Required")

        dataframe["Comment"] = (
            dataframe["ExpectedValue"] + "\n" + dataframe["Vocabulary"]
        )

        # clean special characters
        dataframe["Element name"] = dataframe["Element name"].str.replace("_", ".")

        # lowercase first Element name letter
        dataframe["Element name"] = dataframe["Element name"].map(
            lambda x: x[:1].lower() + x[1:] if (".") not in x else x
        )

        # clean special characterrs
        dataframe["Element name"] = dataframe["Element name"].str.replace(
            "\W", "", regex=True
        )

        # lowercase first Element name letter
        dataframe["dataType"] = dataframe["dataType"].map(
            lambda x: x[:1].lower() + x[1:] if not isinstance(x, float) else x
        )

        # clean codeableconcept
        dataframe["dataType"] = dataframe["dataType"].str.replace(
            "code", "CodeableConcept"
        )
        dataframe["dataType"] = dataframe["dataType"].str.replace(
            "customCode", "CodeableConcept"
        )

        # format codes
        codesList = []

        def formatCodes(x):
            return_string = ""
            for code in re.findall(r"\b\d+\b", str(x)):  # list of codes
                return_string += "$athena#" + str(code) + "\n"
            return return_string

        dataframe["Codes"] = dataframe["Vocabulary"].map(formatCodes)

        # reorder columns
        dataframe = dataframe[COLUMNS_REORDER]

        # Set Index Name
        dataframe.index.name = "Description"

        # dataframe["Codes"] =

        # after conversion write output per sheet
        dataframe.to_excel(writer, sheet_name=xls.sheet_names[sheet_number], index=True)
