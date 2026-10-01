from src.main.python.model.cdm import DrugExposure
from datetime import datetime, date

##print("TEST_MARKER_DRUG_FILE")

DRUG_MAP = {
    'Atorvastatin' :    {'concept_id': 1545958, 'unit_concept_id': 8576},
    'Amlodipine':       {'concept_id':  1332418 , 'unit_concept_id': 8576},
    'Metformin' :        {'concept_id': 1503297, 'unit_concept_id': 8576},
    'Albuterol':         {'concept_id': 1154343, 'unit_concept_id': 45744809},              #actuation 
    'Budesonide_Formoterol':     {'concept_id': 35421281, 'unit_concept_id':None},          #specific concept_id
    'Aspirin' :          {'concept_id': 1112807, 'unit_concept_id': 8576},
    'Topiramate' :         {'concept_id': 742267, 'unit_concept_id': 8576},
    'Sumatriptan' :          {'concept_id': 1140643, 'unit_concept_id': 8576},
    'Lisinopril':            {'concept_id': 1308216, 'unit_concept_id': 8576},
    'Ibuprofen':         {'concept_id': 1177480, 'unit_concept_id': 8576},
    'Paracetamol':       {'concept_id': 1125315, 'unit_concept_id': 8576},
    'Amoxicillin' :      {'concept_id': 1713332, 'unit_concept_id': 8576},
    'Cetirizine':        {'concept_id': 1149196, 'unit_concept_id': 8576},
    'Carvedilol':        {'concept_id': 1346823, 'unit_concept_id': 8576},
    'Furosemide' :       {'concept_id': 956874, 'unit_concept_id': 8576},
    'Pioglitazone' :         {'concept_id': 1525215, 'unit_concept_id': 8576},
    'Levothyroxine':         {'concept_id': 1501700, 'unit_concept_id': 9655},
    'Warfarin':          {'concept_id': 1310149, 'unit_concept_id': 8576},
    'Apixaban':          {'concept_id': 43013024, 'unit_concept_id': 8576},
    'Sertraline':        {'concept_id': 739138, 'unit_concept_id': 8576},
    'Nitroglycerin':         {'concept_id': 1361711, 'unit_concept_id': 8576},
    'Clopidogrel':       {'concept_id': 1322184, 'unit_concept_id': 8576},
    'Semaglutide':       {'concept_id': 793143, 'unit_concept_id': 8576}

}


def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))

def read_drug_dose(dose_str):
    if not dose_str: return None
    number_part = dose_str.split(' ')[0]
    return float(number_part.replace(',', '.'))

def challenge_to_drug(wrapper) -> list:
    data = wrapper.get_challenge_data()
    
    records_to_insert = []
    drug_exposure_id = 1

    for row in data:
        visit_id_numeric = int(row['visit_id'].replace('V', ''))
        person_id = int(row['patient_id'])
        start = read_date(row['drug_exposure_start_date'])
        end = read_date(row['drug_exposure_end_date'])
    
        drug_name = row['drug_name']
        mapping = DRUG_MAP.get(drug_name,{'concept_id': 0, 'unit_concept_id': 0})
    
        if  drug_name == 'Budesonide_Formoterol' : 
            value = None                          # exception double drug
        else:

            value = read_drug_dose(row['drug_dose'])

        record = DrugExposure(
            drug_exposure_id=drug_exposure_id,
            person_id=person_id,
            visit_occurrence_id=visit_id_numeric,

            drug_concept_id=mapping['concept_id'],
            drug_exposure_start_date=start,
            drug_exposure_start_datetime=datetime.combine(start, datetime.min.time()),
            drug_exposure_end_date=end,
            drug_exposure_end_datetime=datetime.combine(end, datetime.min.time()) if end else None,
            drug_type_concept_id=32817,

            route_concept_id = 0,
            quantity = value,

            drug_source_value = drug_name,
            drug_source_concept_id = 0

            )
        records_to_insert.append(record)
        drug_exposure_id +=1

    return records_to_insert


if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_drug(w):
        print(x.__dict__)
    
    
    