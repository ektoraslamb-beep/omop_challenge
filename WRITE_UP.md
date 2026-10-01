# Write up Document  OMOP  ETL


## 1. Design decisions

**Avoiding duplicate records:** The CSV has two rows per patient (one per visit), so duplication was handled per-table depending on what the data represents:

a) *Deduplicated* (static facts repated idetically across both visits): 'Person', 'Observation' (e.g. education, living_situation), 'Death'.
Each keeps only the first occurrence per patient (`seen_patients` set/dict), 
since re-recording an unchanged fact (e.g. gender, marital status, date of death) carries no new information.
`Observation Period` is built directly as one row per patient by construction.

b) *Not-deduplicated* (each row is a genuinely new clinic event): e.g. 'Visit', 'Measurement'. 
A condition or measurement repeated across two visits is treated as two seperate occurrences, not a duplicate of the same record.


**Defining the observation period:** The CSV has no explicit date of the period, so 'observation_period_start/end_date' are derived as the min/max of every event date found across all source tables.

**Coding structure:** Each transformation is a standalone function ('challenge_to_<table>') with its concept mapping as a module-level Python dictionary, given the small size of the dataset(30 rows), a plain dictionary is simpler and easier to review.

**Vocabulary conventions:** Most '_type_concept_id' fields reuse the generic '32817' ("EHR") and Death uses the more specific '32815'. Drug concepts were chosen at Ingredient level so dose stays in 'quantity' rather than baked into the concept name, except 'Budesonide_Formoterol' which is a double drug and had the exact doses in the concept_id.


## 2. Data quality

a) No clinical event (e.g. measurement/condition/procedure) falls outside its patient's 'observation_period' - 0 violations.

b) No clinical event recorded after the death (only one patient 10014, death_date 2024/4/10) - 0 violations.

c) Several source values did not have an exact match in the OHDSI standard vocabulary ('Allergy_Skin_Test' procedure ,'Diet_Type' attribute). The closest available concept was used in each case.


## 3. Final row counts 

*SQL*
SELECT 'person' tbl, COUNT(*) FROM public.person
UNION ALL SELECT 'visit_occurrence', COUNT(*) FROM public.visit_occurrence
UNION ALL SELECT 'observation_period', COUNT(*) FROM public.observation_period
UNION ALL SELECT 'measurement', COUNT(*) FROM public.measurement
UNION ALL SELECT 'condition_occurrence', COUNT(*) FROM public.condition_occurrence
UNION ALL SELECT 'procedure_occurrence', COUNT(*) FROM public.procedure_occurrence
UNION ALL SELECT 'drug_exposure', COUNT(*) FROM public.drug_exposure
UNION ALL SELECT 'observation', COUNT(*) FROM public.observation
UNION ALL SELECT 'death', COUNT(*) FROM public.death;

RESULT 
tbl                 |count|
--------------------+-----+
person              |   15|
visit_occurrence    |   30|
observation_period  |   15|
measurement         |  436|
condition_occurrence|   30|
procedure_occurrence|   30|
drug_exposure       |   30|
observation         |  135|
death               |    1|


## 4. What I would do differently with more time

a) Map the provider and care-site information that exists in the source but was left unmapped.

b) Move the dictionaries to external CSV mapping files (as the existing PRIAS tables do) for easier long-term maintenance.

c) Explore the transformation through the framework's native stem-table routing mechanism, which would make more sense with a larger dataset.

d) Update the stale 'docs' files, which still describe the old PRIAS stem-table architecture (no longer used by this ETL).

e) Deeper vocabulary search on the approximate values rather than accepting the closest match.