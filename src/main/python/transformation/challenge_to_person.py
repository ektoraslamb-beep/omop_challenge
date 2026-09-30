from src.main.python.model.cdm import Person
from datetime import datetime,date


GENDER_MAP = {
    'Male' : 8507,
    'Female' : 8532,
}

RACE_MAP = {
    'White' : 8527,
    'Black' : 8516,
    'Asian' : 8515,
    'Other' : 8522,

}

ETHNICITY_MAP = {
    'Hispanic' : 38003563,
    'Not_Hispanic' : 38003564,

}



def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))



def challenge_to_person(wrapper) -> list:
    data = wrapper.get_challenge_data()

    seen_patients = {}
    for row in data:
        p_id = row['patient_id']
        if p_id not in seen_patients:
            seen_patients[p_id] = row


    records_to_insert = []

    for p_id, row in seen_patients.items():
        birth = read_date(row['birth_date'])
        death = read_date(row['death_date'])

        record = Person(
            person_id = int(p_id),
            person_source_value = p_id,
            gender_concept_id = GENDER_MAP.get(row['gender'], 0),
            gender_source_value = row['gender'],

            year_of_birth = birth.year if birth else None,
            month_of_birth = birth.month if birth else None,
            day_of_birth = birth.day if birth else None,
            birth_datetime = datetime.combine(birth, datetime.min.time()) if birth else None,

            race_concept_id = RACE_MAP.get(row['race'], 0),
            race_source_value = row['race'],

            ethnicity_concept_id = ETHNICITY_MAP.get(row['ethnicity'], 0),
            ethnicity_source_value = row['ethnicity'],

            death_datetime = datetime.combine(death, datetime.min.time()) if death else None,

            gender_source_concept_id = 0,
            race_source_concept_id = 0,
            ethnicity_source_concept_id = 0,
        )
        records_to_insert.append(record)

    return records_to_insert 



if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')  # A mock database object
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_person(w):
        print(x.__dict__)

