from src.main.python.model.cdm import Measurement
from datetime import datetime, date


MEASUREMENT_MAP = {
    'hemoglobin (g/dl)' :   {'concept_id': 3000963, 'unit_concept_id': 8713},
    'ldl (mg/dl)':          {'concept_id': 3028437, 'unit_concept_id': 8840 },
    'Creatinine (mg/dl)' :  {'concept_id': 3016723, 'unit_concept_id': 8840},
    'hdl (mg/dl)' :         {'concept_id': 3007070 , 'unit_concept_id': 8840},
    'systolic_bp (mmhg)' :  {'concept_id': 3004249 , 'unit_concept_id': 8876},
    'diastolic_bp (mmhg)' : {'concept_id': 3012888, 'unit_concept_id': 8876},
    'psa (ng/ml)' :         {'concept_id': 3013603, 'unit_concept_id': 8842},
    'crp (mg/l)' :          {'concept_id': 3020460, 'unit_concept_id': 8751},
    'glucose (mg/dl)' :     {'concept_id': 3004501, 'unit_concept_id': 8840},
    'alt (u/l)' :           {'concept_id': 3006923, 'unit_concept_id': 8645},
    'tsh (uiu/ml)' :        {'concept_id': 3009201, 'unit_concept_id': 9093},
    'platelets (10^9/l)' :  {'concept_id': 3007461, 'unit_concept_id': 9444},
    'vitamin_d (ng/ml)' :   {'concept_id': 3037334, 'unit_concept_id': 8842},
    'potassium (mmol/l)' :  {'concept_id': 3023103, 'unit_concept_id': 8753},
    'bmi (kg/m2)' :         {'concept_id': 3038553, 'unit_concept_id': 9531}

    
}

def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))

def read_nubmer(value_str):
    if not value_str: return None

    return float(value_str.replace(',', '.'))


def challenge_to_measurement(wrapper) -> list:
    data = wrapper.get_challenge_data()

    records_to_insert = []
    measurement_id = 1

    for row in data:
        visit_id_numeric = int(row['visit_id'].replace('V', ''))
        person_id = int(row['patient_id'])
        m_date = read_date(row['measurement_date'])

        for column_name, mapping in MEASUREMENT_MAP.items():
            raw_value = row[column_name]

            if not raw_value: continue

            value = read_nubmer(raw_value)

            record = Measurement(
                measurement_id = measurement_id,
                person_id = person_id,
                visit_occurrence_id = visit_id_numeric,

                measurement_concept_id = mapping['concept_id'],
                measurement_date = m_date,
                measurement_datetime = datetime.combine(m_date, datetime.min.time()),
                measurement_type_concept_id = 32817,

                value_as_number = value,
                unit_concept_id = mapping['unit_concept_id'],

                measurement_source_value = column_name,
                measurement_source_concept_id = 0,
                unit_source_value = column_name
            )
            records_to_insert.append(record)
            measurement_id += 1

    return records_to_insert

if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_measurement(w):
        print(x.__dict__)
