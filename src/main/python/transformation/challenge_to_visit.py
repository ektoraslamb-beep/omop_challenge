from src.main.python.model.cdm import VisitOccurrence
from datetime import datetime, date

VISIT_TYPE_MAP = {
    'outpatient': 9202,
    'inpatient': 9201,
    'emergency': 9203,
}


def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))


def challenge_to_visit(wrapper) -> list:
    data = wrapper.get_challenge_data()

    records_to_insert = []
    for row in data:
        start = read_date(row['visit_start_date'])
        end = read_date(row['visit_end_date'])
        visit_id_numeric = int(row['visit_id'].replace('V', ''))

        record = VisitOccurrence(
            visit_occurrence_id = visit_id_numeric,
            person_id = int(row['patient_id']),

            visit_concept_id = VISIT_TYPE_MAP.get(row['visit_type'], 0),
            visit_source_value = row['visit_type'],
            visit_source_concept_id = 0,

            visit_start_date = start,
            visit_start_datetime = datetime.combine(start, datetime.min.time()),
            visit_end_date = end,
            visit_end_datetime = datetime.combine(end, datetime.min.time()),
            visit_type_concept_id = 32817,

            provider_id = None,
            care_site_id = None,

            discharge_to_concept_id = 0,
            admitted_from_concept_id = 0,

            record_source_value = row['visit_id'],


        )
        records_to_insert.append(record)

    return records_to_insert

if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_visit(w):
        print(x.__dict__)
