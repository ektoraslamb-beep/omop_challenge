# Mapping Document — OMOP CDM v6 (PIONEER variant) ETL

Source: junior_challenge_30.csv (30 rows, 15 patients, 2 visits/patient).
Clinical data schema: `public`. Vocabulary schema: `vocab`.

General convention: all `*_type_concept_id` fields use `32817` ("EHR") as the
generic data-provenance concept, except where noted otherwise (Death). Where
no source-concept mapping was available, `0` ("No matching concept") is used
— e.g. `*_source_concept_id`, `route_concept_id`, `modifier_concept_id`,
`discharge_to_concept_id`, `admitted_from_concept_id`, `condition_status_concept_id`.

---

## Person

| Source column  | Target field                                                  | Concept ID / Mapping                            | Notes                       |
|----------------|---------------------------------------------------------------|-------------------------------------------------|-----------------------------|
| patient_id     | person_id, person_source_value                                |                                                 |                             |
| gender         | gender_concept_id                                             | Male=8507, Female=8532                          |                             |
| birth_date     | year_of_birth, month_of_birth, day_of_birth, birth_datetime   |                                                 |                             |
| race           | race_concept_id                                               | White=8527, Black=8516, Asian=8515, Other=8522  |                             |
| ethnicity      | ethnicity_concept_id                                          | Hispanic=38003563, Not_Hispanic=38003564        |                             |
| death_date     | death_datetime                                                |                                                 | duplicated in `death` table |



## Visit Occurrence

| Source column                      | Target field                                         | Concept ID / Mapping                               | Notes           |
|------------------------------------|----------------------------------------------------- |----------------------------------------------------|-----------------|
| visit_id                           | visit_occurrence_id                                  |                                                    |                 |
| patient_id                         | person_id                                            |                                                    |                 |
| visit_type                         | visit_concept_id                                     | outpatient=9202, inpatient=9201, emergency=9203    |                 |
| visit_start_date / visit_end_date  | visit_start/end_date(time)                           |                                                    |                 |
| visit_id                           | record_source_value                                  |                                                    |                 |
|                                    | visit_type_concept_id                                | 32817                                              |                 |
|                                    | provider_id, care_site_id                            | NULL                                               | not used        |
|                                    | discharge_to_concept_id, admitted_from_concept_id    | 0                                                  | not in source   |

each CSV row = 1 visit (30 rows -> 30 visits).



## Observation Period

Derived per patient as min/max of all event dates in the CSV (visit, measurement,
condition, procedure, drug, observation, death dates).

| Target field                        | Value                        |
|-------------------------------------|------------------------------|
| observation_period_id, person_id    | patient_id                   |
| observation_period_start_date       | min() of all dates           |
| observation_period_end_date         | max() of all dates           |
| period_type_concept_id              | 32817                        |



## Measurement

| Source column          | measurement_concept_id    | unit_concept_id   |
|------------------------|---------------------------|-------------------|
| Hemoglobin (g/dl)      | 3000963                   | 8713              |
| LDL (mg/dl)            | 3028437                   | 8840              |
| Creatinine (mg/dl)     | 3016723                   | 8840              |
| HDL (mg/dl)            | 3007070                   | 8840              |
| Systolic_BP (mmHg)     | 3004249                   | 8876              |
| Diastolic_BP (mmHg)    | 3012888                   | 8876              |
| PSA (ng/ml)            | 3013603                   | 8842              |
| CRP (mg/l)             | 3020460                   | 8751              |
| Glucose (mg/dl)        | 3004501                   | 8840              |
| ALT (u/l)              | 3006923                   | 8645              |
| TSH (uIU/ml)           | 3009201                   | 9093              |
| Platelets (10^9/l)     | 3007461                   | 9444              |
| Vitamin_D (ng/ml)      | 3037334                   | 8842              |
| Potassium (mmol/l)     | 3023103                   | 8753              |
| BMI (kg/m2)            | 3038553                   | 9531              |

measurement_type_concept_id = 32817



## Condition Occurrence

| Source value (condition_name)    | condition_concept_id   |
|----------------------------------|------------------------|
| Hypertension                     | 316866                 |
| Type_2_Diabetes                  | 201826                 |
| Asthma                           | 317009                 |
| Coronary_Artery_Disease          | 317576                 |
| Migraine                         | 318736                 |
| Chronic_Kidney_Disease           | 46271022               |
| Osteoarthritis                   | 80180                  |
| Acute_Bronchitis                 | 260139                 |
| Allergic_Rhinitis                | 257007                 |
| Heart_Failure                    | 316139                 |
| Fatty_Liver                      | 4026131                |
| Hypothyroidism                   | 140673                 |
| Deep_Vein_Thrombosis             | 4133004                |
| Anxiety_Disorder                 | 442077                 |
| Stable_Angina                    | 4119942                |
| Myocardial_Infarction            | 4329847                |
| Obesity                          | 433736                 |

condition_type_concept_id = 32817. 



## Procedure Occurrence

| Source value (procedure_name)     | procedure_concept_id    | Notes                                      |
|-----------------------------------|-------------------------|--------------------------------------------|
| Colonoscopy                       | 4249893                 |                                            |
| Ambulatory_BP_Monitoring          | 40491004                |                                            |
| Appendectomy                      | 4198190                 |                                            |
| Diabetic_Retinal_Exam             | 36716226                |                                            |
| Bronchoscopy                      | 4032404                 |                                            |
| Spirometry                        | 4133840                 |                                            |
| Cardiac_Catheterization           | 4223020                 |                                            |
| Stress_Test                       | 4296597                 |                                            |
| Neurological_Examination          | 4225119                 |                                            |
| MRI_Brain                         | 4013636                 | generic "MRI", not brain-specific          |
| Renal_Biopsy                      | 4217034                 |                                            |
| Renal_Ultrasound                  | 42535005                | bilateral kidney concept                   |
| Knee_Arthroscopy                  | 4205229                 |                                            |
| Physiotherapy                     | 4145658                 |                                            |
| Chest_XRay                        | 4163872                 |                                            |
| Allergy_Skin_Test                 | 0                       | no Procedure-domain concept found          |
| Echocardiogram                    | 4230911                 |                                            |
| Liver_Ultrasound                  | 4023136                 |                                            |
| Liver_Elastography                | 40479203                |                                            |
| Thyroid_Ultrasound                | 4198775                 | includes parathyroid                       |
| Physical_Examination              | 4240345                 |                                            |
| Venous_Doppler                    | 46272013                |                                            |
| Psychotherapy                     | 4327941                 |                                            |
| Exercise_Stress_Test              | 4296597                 | reused Stress_Test concept                 |
| PCI                               | 4216130                 |                                            |
| Dietary_Counseling                | 37150967                | "Development of nutrition care plan"       |

procedure_type_concept_id = 32817, modifier_concept_id = 0. 



## Drug Exposure

| Source value (drug_name) | drug_concept_id | unit_concept_id | Notes                                                  |
|------------------------------|---------------------|--------------------|---------------------------------------------|
| Atorvastatin                 | 1545958             | 8576               |                                             |
| Amlodipine                   | 1332418             | 8576               |                                             |
| Metformin                    | 1503297             | 8576               |                                             |
| Albuterol                    | 1154343             | 45744809           | unit = Actuation (puffs)                    |
| Budesonide_Formoterol        | 35421281            |                    | combination dose baked into concept name    |
| Aspirin                      | 1112807             | 8576               |                                             |
| Topiramate                   | 742267              | 8576               |                                             |
| Sumatriptan                  | 1140643             | 8576               |                                             |
| Lisinopril                   | 1308216             | 8576               |                                             |
| Ibuprofen                    | 1177480             | 8576               |                                             |
| Paracetamol                  | 1125315             | 8576               | mapped via Acetaminophen (RxNorm)           |
| Amoxicillin                  | 1713332             | 8576               |                                             |
| Cetirizine                   | 1149196             | 8576               |                                             |
| Carvedilol                   | 1346823             | 8576               |                                             |
| Furosemide                   | 956874              | 8576               |                                             |
| Pioglitazone                 | 1525215             | 8576               |                                             |
| Levothyroxine                | 1501700             | 9655               |                                             |
| Warfarin                     | 1310149             | 8576               |                                             |
| Apixaban                     | 43013024            | 8576               |                                             |
| Sertraline                   | 739138              | 8576               |                                             |
| Nitroglycerin                | 1361711             | 8576               |                                             |
| Clopidogrel                  | 1322184             | 8576               |                                             |
| Semaglutide                  | 793143              | 8576               |                                             |

drug_type_concept_id = 32817, route_concept_id = 0.



## Observation

Pattern: one attribute-level concept per column + one value-level map per column.

| CSV column              | observation_concept_id      | Value map                                                                      |
|-------------------------|-----------------------------|--------------------------------------------------------------------------------|
| Smoking_Status          | 648645                      | Current=45881517, Former=45883458, Never=45879404                              |
| Alcohol_Use             | 648994                      | Heavy=4336673, Moderate=4183729, Occasional=4027342, None=4022664              |
| Exercise_Level          | 44808782                    | High=44792782, Moderate=44792781, Low=44792757                                 |
| Living_Situation        | 3051968                     | Alone=4023168, With_Family=4076105, With_Partner=4248956                       |
| Diet_Type               | 40763905                    | Mediterranean=37150978, Omnivore=4109841, Vegan=40299152, Vegetarian=35622818  |
| Employment_Status       | 36304255                    | Employed=4076340, Retired=4022069, Self_Employed=4059636, Unemployed=4251171   |
| Marital_Status          | 3046344                     | Divorced=4069297, Married=4338692, Single=4053842, Widowed=4143188             |
| Education_Level         | 36031310                    | College=4072737, High_School=43021808, Postgraduate=4260255                    |
| nationality             | 1092097                     | Austria=4329596, Belgium=45876282, Denmark=41917250, Finland=4320323, France=41928898, Germany=41970930, Greece=45878321, Ireland=4330438, Italy=41987173, Netherlands=45882461, Poland=45878488, Portugal=4320170, Spain=42020824, Sweden=45878486, United_Kingdom=45880074 |

 observation_type_concept_id = 32817

## Death

| Source column | Target field                                                        | Value                         |
|-----------------|-------------------------------------------------------------------|-------------------------------|
|death_date       | death_date, death_datetime                                        |                              |
|                 | death_type_concept_id                                             | 32815 ("Death Certificate")   |
|                 | cause_concept_id, cause_source_value, cause_source_concept_id     | NULL                          |