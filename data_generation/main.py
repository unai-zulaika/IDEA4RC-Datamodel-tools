import pandas as pd
from tqdm import tqdm
import re
import random
from datetime import datetime, timedelta


def get_random_date(start_date: str, end_date: str) -> str:
    # Parse the input strings into datetime objects
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate the range of days between the two dates
    delta = (end - start).days

    # Generate a random number of days to add to the start date
    random_days = random.randint(0, delta)

    # Calculate the random date and return it in YYYY-MM-DD format
    random_date = start + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def add_random_days(date: str, min_days: int, max_days: int) -> str:
    # Parse the input date string into a datetime object
    base_date = datetime.strptime(date, "%Y-%m-%d")

    # Generate a random number of days within the range
    random_days = random.randint(min_days, max_days)

    # Add the random number of days to the date
    new_date = base_date + timedelta(days=random_days)

    # Return the resulting date in YYYY-MM-DD format
    return new_date.strftime("%Y-%m-%d")


def read_sheet(
    normalized_table, xls, sheet_number, cur_date, p_id, record_id, linked_to_element
):
    dataframe = pd.read_excel(xls, sheet_name=sheet_number)

    for _, row in dataframe.iterrows():
        # Example data for the new row
        core_variable = f"{row['ObjectClass']}.{row['ObjectProperty']}"
        datatype = row["FormatConceptualDomain"]

        value = ""
        if datatype in ["Code", "CodeableConcept"]:
            if not pd.isna(row["Vocabulary"]):
                codes = re.findall(r"\b\d+\b", row["Vocabulary"])
                if codes:
                    value = random.choice(codes)
        if datatype in ["Boolean"]:
            value = random.choice([True, False])
        if datatype in ["Integer"]:
            value = random.randint(1, 100)
        if datatype in ["Float"]:
            value = random.uniform(1, 100)
        if datatype in ["Date"]:
            value = cur_date
            cur_date = add_random_days(cur_date, MIN_DIFF_DAYS, MAX_DIFF_DAYS)

        data = {
            "patient_id": p_id,
            "original_source": "synthetic",
            "core_variable": core_variable,
            "date_ref": "",
            "value": value,
            "record_id": record_id,
            "linked_to": linked_to_element,
            "quality": "",
            "types": datatype,
        }

        row = pd.DataFrame([data])  # Wrap data in a list for proper DataFrame creation
        normalized_table = pd.concat([normalized_table, row], ignore_index=True)
    return row, cur_date, normalized_table


SHEET_ID = "1ANErBpHQAW6ngn1kq-a7rPpeTosG-z2PHnwfUT6IUKI"

# Load data model
SHEETS_TO_PROCESS = list(range(8, 27))
OUTPUT_FILEPATH = "synthetic_idea4rc.xlsx"
PATIENT_AMOUNT = 100
INIT_START_DATE = "1995-01-01"
INIT_END_DATE = "2020-01-01"
MIN_DIFF_DAYS = 5
MAX_DIFF_DAYS = 30

# Load file
xls = pd.ExcelFile(
    f"https://docs.google.com/spreadsheets/export?id={SHEET_ID}&format=xlsx"
)

nt_columns = [
    "patient_id",
    "original_source",
    "core_variable",
    "date_ref",
    "value",
    "record_id",
    "linked_to",
    "quality",
    "types",
]

index_to_sheetname = {
    8: 1,  # "Patient",
    9: [1, 10],
    10: 0,
    11: 0,
    12: 1,  # CancerEpisode
    13: 1,  # Diag
    14: 1,  # CS
    15: 1,  # PS
    16: [1, 5],  # "EpisodeEvent",
    17: [1, 5],  # DiseaseExtent
    18: 1,  # GTE
    19: [0, 3],  # Surgery
    20: [0, 3],  # ST
    21: [0, 3],  # RT
    22: 0,  # RDH
    23: 0,  # ILP
    24: "",  # DrugsForTreatments
    25: "",  # OTR
    26: "",  # AE
}

# Create Normalized table
normalized_table = pd.DataFrame(columns=nt_columns)

# file = pd.ExcelFile(xls)
# print(file.sheet_names)
# exit()

record_id = 0  # increase each time

for p_id in tqdm(range(PATIENT_AMOUNT)):
    cur_date = random_date = get_random_date(INIT_START_DATE, INIT_END_DATE)

    # First the patient
    row, cur_date_mod, normalized_table_mod = read_sheet(
        normalized_table, xls, 8, cur_date, p_id, record_id, ""
    )
    normalized_table = normalized_table_mod
    cur_date = cur_date_mod
    patient_element = record_id
    record_id += 1

    # Second the CancerEpisode
    row, cur_date_mod, normalized_table_mod = read_sheet(
        normalized_table, xls, 12, cur_date, p_id, record_id, patient_element
    )
    normalized_table = normalized_table_mod
    cur_date = cur_date_mod
    ce_element = record_id
    record_id += 1

    # Third the Diagnosis and PathologicalStage and ClinicalStage
    row, cur_date_mod, normalized_table_mod = read_sheet(
        normalized_table, xls, 13, cur_date, p_id, record_id, ce_element
    )
    normalized_table = normalized_table_mod
    cur_date = cur_date_mod
    diagnosis_element = record_id
    record_id += 1

    row, cur_date_mod, normalized_table_mod = read_sheet(
        normalized_table, xls, 14, cur_date, p_id, record_id, diagnosis_element
    )
    normalized_table = normalized_table_mod
    cur_date = cur_date_mod
    record_id += 1

    row, cur_date_mod, normalized_table_mod = read_sheet(
        normalized_table, xls, 15, cur_date, p_id, record_id, diagnosis_element
    )
    normalized_table = normalized_table_mod
    cur_date = cur_date_mod
    record_id += 1

    # for each of N EpisodeEvents and DiseaseExtent -> treatments and OverallTreatmentResponse
    for i in range(random.choice([1, 2, 3, 4, 5, 6])):
        row, cur_date_mod, normalized_table_mod = read_sheet(
            normalized_table, xls, 16, cur_date, p_id, record_id, ce_element
        )
        normalized_table = normalized_table_mod
        cur_date = cur_date_mod
        ee_element = record_id
        record_id += 1

        row, cur_date_mod, normalized_table_mod = read_sheet(
            normalized_table, xls, 17, cur_date, p_id, record_id, ee_element
        )
        normalized_table = normalized_table_mod
        cur_date = cur_date_mod
        record_id += 1

        # roll a dice, up to 4 treatments
        for i in range(random.choice([1, 2, 3, 4])):
            # roll a dice to choose between Surgery, SystemicTreatment, Radiotherapy
            treatment_type = random.choice([19, 20, 21])
            row, cur_date_mod, normalized_table_mod = read_sheet(
                normalized_table,
                xls,
                treatment_type,
                cur_date,
                p_id,
                record_id,
                diagnosis_element if i == 0 else ee_element,
            )
            normalized_table = normalized_table_mod
            cur_date = cur_date_mod
            record_id += 1

        # OTR
        row, cur_date_mod, normalized_table_mod = read_sheet(
            normalized_table,
            xls,
            25,
            cur_date,
            p_id,
            record_id,
            diagnosis_element if i == 0 else ee_element,
        )
        normalized_table = normalized_table_mod
        cur_date = cur_date_mod
        record_id += 1

        # Read each sheet
        """ dataframe = pd.read_excel(xls, sheet_name=sheet_number)
        le = 1
        if index_to_sheetname[sheet_number] == "N":
            le = random.choice([1, 2, 3])
            print(f"Generating {le} records for patient {p_id}")
        for examples in range(le):
            for index, row in dataframe.iterrows():
                # Example data for the new row
                core_variable = f"{row['ObjectClass']}.{row['ObjectProperty']}"
                datatype = row["FormatConceptualDomain"]

                value = ""
                if datatype in ["Code", "CodeableConcept"]:
                    if not pd.isna(row["Vocabulary"]):
                        codes = re.findall(r"\b\d+\b", row["Vocabulary"])
                        if codes:
                            value = random.choice(codes)
                if datatype in ["Boolean"]:
                    value = random.choice([True, False])
                if datatype in ["Integer"]:
                    value = random.randint(1, 100)
                if datatype in ["Float"]:
                    value = random.uniform(1, 100)
                if datatype in ["Date"]:
                    value = cur_date
                    cur_date = add_random_days(cur_date, MIN_DIFF_DAYS, MAX_DIFF_DAYS)

                data = {
                    "patient_id": p_id,
                    "original_source": "synthetic",
                    "core_variable": core_variable,
                    "date_ref": "",
                    "value": value,
                    "record_id": record_id,
                    "linked_to": "",
                    "quality": "",
                    "types": datatype,
                }

                row = pd.DataFrame(
                    [data]
                )  # Wrap data in a list for proper DataFrame creation

                # Append to the normalized table, could we do it only at the end?
                normalized_table = pd.concat([normalized_table, row], ignore_index=True)
            record_id += 1 """


# Save to Excel
normalized_table.to_excel(OUTPUT_FILEPATH, index=False)
