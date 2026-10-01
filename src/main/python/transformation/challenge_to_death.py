from src.main.python.model.cdm import Death
from datetime import datetime,date


def read_date(date_str):
    if not date_str:
        return None
    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))


def challenge_to_death(wrapper) -> list:
    data = wrapper.get_challenge_data()
    records_to_insert = []
    seen_patients = set()

    for row in data:
        person_id = int(row['patient_id'])
        death_date = read_date(row['death_date'])
        death_date_str = row['death_date']

        if not death_date_str:
            continue

        if person_id in seen_patients:
            continue
        seen_patients.add(person_id)

        record = Death(
            person_id = person_id,
            death_date = death_date,

            death_datetime = datetime.combine(death_date,datetime.min.time()),
            death_type_concept_id =32815

        )
        records_to_insert.append(record)

    return records_to_insert



if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_death(w):
        print(x.__dict__)
