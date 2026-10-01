from src.main.python.model.cdm import Observation
from datetime import datetime,date


SMOKING_OBSERVATION_CONCEPT_ID = 648645          
ALCOHOL_OBSERVATION_CONCEPT_ID = 648994             
EXERCISE_OBSERVATION_CONCEPT_ID = 44808782             
LIVING_OBSERVATION_CONCEPT_ID = 3051968              
DIET_OBSERVATION_CONCEPT_ID = 40763905                  # Diet and nutrition Narrative           
EMPLOYMENT_OBSERVATION_CONCEPT_ID = 36304255          
MARITAL_OBSERVATION_CONCEPT_ID = 3046344            
EDUCATION_OBSERVATION_CONCEPT_ID = 36031310           
NATIONALITY_OBSERVATION_CONCEPT_ID = 1092097        





SMOKING_VALUE_MAP = {
    'Current': 45881517,  
    'Former': 45883458,    
    'Never': 45879404,     
}


ALCOHOL_VALUE_MAP = {
    'Heavy': 4336673,       
    'Moderate': 4183729,    
    'Occasional': 4027342,  
    'None': 4022664,        
}


EXERCISE_VALUE_MAP = {
    'High': 44792782,     
    'Low': 44792757,       
    'Moderate': 44792781,  
}


LIVING_VALUE_MAP = {
    'Alone': 4023168,        
    'With_Family': 4076105, 
    'With_Partner': 4248956,
}


DIET_VALUE_MAP = {
    'Mediterranean': 37150978, 
    'Omnivore': 4109841,       
    'Vegan': 40299152,          
    'Vegetarian': 35622818,     
}


EMPLOYMENT_VALUE_MAP = {
    'Employed': 4076340,       
    'Retired': 4022069,       
    'Self_Employed': 4059636, 
    'Unemployed': 4251171,     
}


MARITAL_VALUE_MAP = {
    'Divorced': 4069297, 
    'Married': 4338692,   
    'Single': 4053842,    
    'Widowed': 4143188,  
}


EDUCATION_VALUE_MAP = {
    'College': 4072737,      
    'High_School': 43021808,  
    'Postgraduate': 4260255, 
}


NATIONALITY_VALUE_MAP = {
    'Austria': 4329596, 'Belgium': 45876282, 'Denmark': 41917250, 'Finland': 4320323,
    'France': 41928898, 'Germany': 41970930, 'Greece': 45878321, 'Ireland': 4330438,
    'Italy': 41987173, 'Netherlands': 45882461, 'Poland': 45878488, 'Portugal': 4320170,
    'Spain': 42020824, 'Sweden': 45878486, 'United_Kingdom': 45880074,  
}

COLUMN_CONFIG = {
    'Smoking_Status':    {'observation_concept_id': SMOKING_OBSERVATION_CONCEPT_ID,    'value_map': SMOKING_VALUE_MAP},
    'Alcohol_Use':       {'observation_concept_id': ALCOHOL_OBSERVATION_CONCEPT_ID,     'value_map': ALCOHOL_VALUE_MAP},
    'Exercise_Level':    {'observation_concept_id': EXERCISE_OBSERVATION_CONCEPT_ID,    'value_map': EXERCISE_VALUE_MAP},
    'Living_Situation':  {'observation_concept_id': LIVING_OBSERVATION_CONCEPT_ID,      'value_map': LIVING_VALUE_MAP},
    'Diet_Type':         {'observation_concept_id': DIET_OBSERVATION_CONCEPT_ID,        'value_map': DIET_VALUE_MAP},
    'Employment_Status': {'observation_concept_id': EMPLOYMENT_OBSERVATION_CONCEPT_ID,  'value_map': EMPLOYMENT_VALUE_MAP},
    'Marital_Status':    {'observation_concept_id': MARITAL_OBSERVATION_CONCEPT_ID,     'value_map': MARITAL_VALUE_MAP},
    'Education_Level':   {'observation_concept_id': EDUCATION_OBSERVATION_CONCEPT_ID,   'value_map': EDUCATION_VALUE_MAP},
    'nationality':       {'observation_concept_id': NATIONALITY_OBSERVATION_CONCEPT_ID, 'value_map': NATIONALITY_VALUE_MAP},
}


def read_date(date_str):
    if not date_str:
        return None
    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))


def challenge_to_observation(wrapper) -> list:
    data = wrapper.get_challenge_data()

    records_to_insert = []
    observation_id = 1
    seen_patients = set()   

    for row in data:
        person_id = int(row['patient_id'])

        if person_id in seen_patients:
            continue   

        seen_patients.add(person_id)

        visit_id_numeric = int(row['visit_id'].replace('V', ''))
        obs_date = read_date(row['observation_date'])

        for column_name, config in COLUMN_CONFIG.items():
            raw_value = row[column_name]
            if not raw_value:
                continue

            value_concept_id = config['value_map'].get(raw_value, 0)

            record = Observation(
                observation_id=observation_id,
                person_id=person_id,
                visit_occurrence_id=visit_id_numeric,

                observation_concept_id=config['observation_concept_id'],
                observation_date=obs_date,
                observation_datetime=datetime.combine(obs_date, datetime.min.time()),
                observation_type_concept_id=32817,

                value_as_string=raw_value,
                value_as_concept_id=value_concept_id,

                observation_source_value=raw_value,
                observation_source_concept_id=0,
                obs_event_field_concept_id=0,
            )

            records_to_insert.append(record)
            observation_id += 1

    return records_to_insert





if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_observation(w):
        print(x.__dict__)