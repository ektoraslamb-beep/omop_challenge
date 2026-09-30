from src.main.python.model.cdm import ConditionOccurrence
from datetime import datetime, date

CONDITION_MAP = {
    'Hypertension' :        316866,
    'Type_2_Diabetes' :     201826,
    'Asthma' :              317009,
    'Coronary_Artery_Disease':317576,
    'Migraine':              318736,
    'Chronic_Kidney_Disease': 46271022,
    'Osteoarthritis':       80180,
    'Acute_Bronchitis':     260139,
    'Allergic_Rhinitis':    257007,
    'Heart_Failure':        316139,
    'Fatty_Liver' :         4026131,
    'Hypothyroidism' :      140673,
    'Deep_Vein_Thrombosis' : 4133004,
    'Anxiety_Disorder' :    442077,
    'Stable_Angina' :       4119942,
    'Myocardial_Infarction' : 4329847,
    'Obesity' :             433736

}

def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))

def challenge_to_condition(wrapper) -> list:
    data = wrapper.get_challenge_data()

    records_to_insert = []
    condition_occurrence_id = 1

    for row in data:
        visit_id_numeric = int(row['visit_id'].replace('V', ''))
        person_id = int(row['patient_id'])

        condition_name = row['condition_name']
        start = read_date(row['condition_start_date'])
        end = read_date(row['condition_end_date'])

        concept_id = CONDITION_MAP.get(condition_name, 0)

        record = ConditionOccurrence(
            condition_occurrence_id = condition_occurrence_id,
            person_id = person_id,

            visit_occurrence_id = visit_id_numeric,
            condition_concept_id = concept_id,
            condition_start_date=start,
            condition_start_datetime=datetime.combine(start, datetime.min.time()),
            condition_end_date=end,
            condition_end_datetime=datetime.combine(end, datetime.min.time()) if end else None,
            condition_type_concept_id=32817,

            condition_source_value = condition_name,
            condition_status_concept_id = 0,
            condition_source_concept_id = 0
        )

        records_to_insert.append(record)
        condition_occurrence_id += 1
    return records_to_insert


if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_condition(w):
        print(x.__dict__)