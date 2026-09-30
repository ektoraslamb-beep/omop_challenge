from src.main.python.model.cdm import ProcedureOccurrence
from datetime import datetime, date


PROCEDURE_MAP = {
    'Colonoscopy' :     4249893,
    'Ambulatory_BP_Monitoring' :   40491004 ,
    'Appendectomy' :        4198190, 
    'Diabetic_Retinal_Exam' :   36716226,
    'Bronchoscopy' :        4032404,
    'Spirometry' :          4133840,
    'Cardiac_Catheterization' :     4223020,
    'Stress_Test' :         4296597,
    'Neurological_Examination' :    4225119,
    'MRI_Brain' :           4013636,                    #just MRI
    'Renal_Biopsy' :        4217034,
    'Renal_Ultrasound' :        42535005,               #both kidneys
    'Knee_Arthroscopy' :        4205229,
    'Physiotherapy' :       4145658,
    'Chest_XRay' :      4163872,
    'Allergy_Skin_Test' :   0,                  #Condition ("Allergic disorder of skin", "Anaphylaxis caused by allergy skin test")
    'Echocardiogram' :      4230911,
    'Liver_Ultrasound' :    4023136,
    'Liver_Elastography' :  40479203,
    'Thyroid_Ultrasound' :      4198775,            # Ultrasonography of thyroid and parathyroid       
    'Physical_Examination' :       4240345,
    'Venous_Doppler' :      46272013,
    'Psychotherapy' :       4327941,
    'Exercise_Stress_Test' :    4296597,           #same with stess test, Exercise stress echocardiography closest
    'PCI' :             4216130,
    'Dietary_Counseling' : 37150967                 #not exactlly, Development of nutrition care plan     
    
 
}


def read_date(date_str):
    if not date_str: return None

    month, day, year = date_str.split('/')
    return date(int(year), int(month), int(day))


def challenge_to_procedure(wrapper) -> list:
    data = wrapper.get_challenge_data()

    records_to_insert = []
    procedure_occurrence_id = 1

    for row in data:
        visit_id_numeric = int(row['visit_id'].replace('V',''))
        person_id = int(row['patient_id'])

        procedure_name = row['procedure_name']
        p_date = read_date(row['procedure_date'])


        concept_id = PROCEDURE_MAP.get(procedure_name, 0)

        record = ProcedureOccurrence(
            procedure_occurrence_id = procedure_occurrence_id,
            person_id = person_id,
            visit_occurrence_id = visit_id_numeric,

            procedure_concept_id = concept_id,
            procedure_date = p_date,
            procedure_datetime = datetime.combine(p_date, datetime.min.time()),
            procedure_type_concept_id = 32817,


            procedure_source_value = procedure_name,
            procedure_source_concept_id = 0,
            modifier_concept_id = 0



        )
        records_to_insert.append(record)

        procedure_occurrence_id += 1
    return records_to_insert



if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_30', '../../../../resources/mapping_tables')

    for x in challenge_to_procedure(w):
        print(x.__dict__)