from src.main.python.model.cdm import ObservationPeriod
from datetime import datetime, date



def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))


def challenge_to_observation_period(wrapper) -> list:
    data = wrapper.get_challenge_data()

    DATE_COLUMNS = [
        'visit_start_date', 'visit_end_date',
        'measurement_date',
        'condition_start_date','condition_end_date',
        'procedure_date',
        'drug_exposure_start_date','drug_exposure_end_date',
        'observation_date',
        'death_date'
    ]

    patient_dates = {}

    for row in data:
        p_id = row['patient_id']
        if p_id not in patient_dates:
            patient_dates[p_id] = []

        for col in DATE_COLUMNS:
            d = read_date(row[col])

            if d:
                patient_dates[p_id].append(d)


    records_to_insert = []
    for p_id, dates in patient_dates.items():
        record = ObservationPeriod(
            observation_period_id = int(p_id),
            person_id = int(p_id),
            observation_period_start_date = min(dates),
            observation_period_end_date = max(dates),
            period_type_concept_id = 32817
        )
        records_to_insert.append(record)

    return records_to_insert



if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_observation_period(w):
        print(x.__dict__)
