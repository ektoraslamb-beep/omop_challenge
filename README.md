# OMOP Data Engineering Challenge

Welcome! In this challenge you will build an ETL that converts a small, synthetic clinical dataset into the
[OMOP Common Data Model](https://ohdsi.github.io/CommonDataModel/). The repository contains a working
reference ETL (for the PRIAS prostate cancer registry, targeting a PIONEER modification of
[OMOP CDM v6.x](https://github.com/thehyve/ohdsi-omop-pioneer/tree/master/pioneer_omop_cdm) with the
[Oncology WG extensions](https://github.com/OHDSI/OncologyWG/wiki)). Use it as a template for the framework and
code style. **Your job is to write the transformations for a new source dataset.**

The PRIAS mapping document (useful as an example of what a mapping document looks like) is
[here](https://thehyve.github.io/ohdsi-etl-prias/) and in [`docs/`](docs/).

---

## 1. Prerequisites

- Docker Desktop
- Visual Studio Code (or another editor)
- pgAdmin, DBeaver or `psql` for exploring the database
- An [Athena](https://athena.ohdsi.org/) account (free) to download the OMOP vocabularies
- Optional: Python 3.9 if you want to run the ETL outside Docker (same version as the ETL `Dockerfile`)

## 2. Setup

### 2.1 Vocabulary

1. In Athena, go to **Download** and select at least these vocabularies:
   **SNOMED, LOINC, RxNorm, RxNorm Extension, UCUM, Gender, Race, Ethnicity, Visit, Type Concept**.
   Do **not** select CPT4. A CPT4 concept file is already included in `postgres/CONCEPT_CPT4.csv`, and adding it again creates duplicate concepts.
2. When the download is ready, rename the `.zip` to `vocabulary.zip` and place it in the `postgres/` folder.

On first start, the database loads the vocabulary into the **`vocab`** schema (`vocab.concept`,
`vocab.concept_relationship`, …). This can take 10–30 minutes.

### 2.2 Docker

```bash
cd postgres
docker build -t thehyve/ohdsi_postgresql .     # note the trailing dot
cd ..
docker compose up -d
```

This starts `postgresql`, `broadsea-webtools`, `broadsea-methods-library`, `jupyter` and `etl`.
Only `postgresql` and `etl` are needed for this challenge.

Follow progress with:

```bash
docker compose logs -f postgresql
docker compose logs -f etl
```

Database connection (from your host): `localhost:5432`, database `ohdsi`, user `admin`, password `secret`.

> The Postgres init scripts (and therefore the vocabulary load) **only run when the data volume is empty**.
> If the vocabulary load failed, remove the volume and start again: `docker compose down -v`, then `docker compose up -d`.

### 2.3 Troubleshooting on Windows

If the postgres logs show `/bin/sh^M: bad interpreter: No such file or directory`, then
`postgres/10-init-vocabulary.sh` has Windows (CRLF) line endings. In VS Code, click `CRLF` in the status bar,
switch it to `LF`, save, and rebuild (`docker compose down -v`, then `docker compose up --build -d`).

---

## 3. The challenge dataset

| | |
|---|---|
| File | `resources/test_datasets/junior_challenge_30/junior_challenge_30.csv` |
| Rows | 30 (plus header) |
| Patients | 15 (`patient_id` 10001–10015) |
| Grain | **One row = one visit.** Every patient has exactly 2 visits. Patient-level columns are repeated on both rows. |
| Columns | 47 |

### 3.1 File format (read this carefully)

- **Delimiter:** semicolon `;`
- **Encoding:** UTF-8 **with BOM**
- **Decimal separator:** comma, everywhere (`13,8` = 13.8; `12,5 mg` = 12.5 mg)
- **Date format:** `M/D/YYYY` (US style, no leading zeros), e.g. `12/25/2023` = 25 December 2023
- **Line endings:** CRLF
- Empty string = missing value

> The existing `SourceData` class (`src/main/python/model/SourceData.py`) reads files as Windows-1252 with a
> comma delimiter by default. It will **not** read this file correctly as-is. Check what the parsed header and
> values look like before building on them.

### 3.2 Column dictionary

**Patient-level (repeated on each row of the patient)**

| Column | Example | Notes |
|---|---|---|
| `patient_id` | `10001` | Source patient identifier |
| `gender` | `Male`, `Female` | |
| `birth_date` | `5/14/1975` | Full date of birth |
| `race` | `White`, `Black`, `Asian`, `Other` | |
| `ethnicity` | `Hispanic`, `Not_Hispanic` | |
| `nationality` | `Netherlands`, `United_Kingdom`, … | |
| `death_date` | `3/1/2024` or empty | Empty if the patient is alive |

**Visit-level**

| Column | Example | Notes |
|---|---|---|
| `visit_id` | `V1001` | Unique per row |
| `visit_type` | `outpatient`, `inpatient`, `emergency` | |
| `visit_start_date`, `visit_end_date` | `2/10/2024`, `2/13/2024` | |
| `provider_id` | `PR1` | Source provider code |
| `care_site_id` | `CS1` | Source care site code |

**Measurements.** One value per visit, all taken on `measurement_date`. The unit is in the column header.

| Column | Unit |
|---|---|
| `Hemoglobin (g/dL)` | g/dL |
| `LDL (mg/dL)` | mg/dL |
| `Creatinine (mg/dL)` | mg/dL |
| `HDL (mg/dL)` | mg/dL |
| `Systolic_BP (mmHg)` | mmHg |
| `Diastolic_BP (mmHg)` | mmHg |
| `PSA (ng/mL)` | ng/mL (prostate marker: empty for female patients) |
| `CRP (mg/L)` | mg/L |
| `Glucose (mg/dL)` | mg/dL |
| `ALT (U/L)` | U/L |
| `TSH (uIU/mL)` | µIU/mL |
| `Platelets (10^9/L)` | 10^9/L |
| `Vitamin_D (ng/mL)` | ng/mL |
| `Potassium (mmol/L)` | mmol/L |
| `BMI (kg/m2)` | kg/m² |
| `measurement_date` | date of the measurements above |

**Condition, procedure and drug (one of each per row)**

| Column | Example | Notes |
|---|---|---|
| `condition_name` | `Type_2_Diabetes` | Free-text-like label (underscores instead of spaces) |
| `condition_start_date` | `3/20/2019` | Can be years before the visit |
| `condition_end_date` | `5/17/2024` or empty | Empty = ongoing |
| `procedure_name` | `Appendectomy` | |
| `procedure_date` | `2/12/2024` | |
| `drug_name` | `Metformin` | Ingredient name |
| `drug_dose` | `500 mg`, `2 puffs`, `160/4,5 mcg` | Free text, not always "number + unit" |
| `drug_exposure_start_date`, `drug_exposure_end_date` | `2/14/2024`, `2/13/2025` | |

**Observations (lifestyle and social).** All recorded on `observation_date`.

| Column | Values |
|---|---|
| `Smoking_Status` | `Never`, `Former`, `Current` |
| `Alcohol_Use` | `None`, `Occasional`, `Moderate`, `Heavy` |
| `Exercise_Level` | `Low`, `Moderate`, `High` |
| `Living_Situation` | `Alone`, `With_Partner`, `With_Family` |
| `Diet_Type` | `Omnivore`, `Vegetarian`, `Vegan`, `Mediterranean` |
| `Employment_Status` | `Employed`, `Self_Employed`, `Unemployed`, `Retired` |
| `Marital_Status` | `Single`, `Married`, `Divorced`, `Widowed` |
| `Education_Level` | `High_School`, `College`, `Postgraduate` |
| `observation_date` | date of the observations above |

> Profile the data before you map it. Because the file is "wide" (one row per visit), some facts are
> repeated on both rows of a patient. For example, a chronic condition or the lifestyle answers appear at every
> visit. Some dates also fall outside the visit itself, such as condition start dates years in the past, or drug
> exposures that run long after the visit. Decide how to handle these (deduplicate? link to a visit?), and
> **document your decisions**.

---

## 4. What you need to do

### 4.1 Required output (OMOP tables in the `public` schema)

| OMOP table | Source |
|---|---|
| `person` | patient-level columns (one record per patient) |
| `observation_period` | derived: decide and document how you define the period |
| `visit_occurrence` | visit-level columns (one record per `visit_id`) |
| `measurement` | the 15 measurement columns |
| `condition_occurrence` | `condition_*` columns |
| `procedure_occurrence` | `procedure_*` columns |
| `drug_exposure` | `drug_*` columns |
| `observation` | lifestyle and social columns (and anything else that has no better home, e.g. nationality) |
| death | record `death_date` (in CDM v6 this is `person.death_datetime`; a `death` table also exists in this repo) |

Use **standard concepts** where they exist (SNOMED for conditions and procedures, LOINC for measurements,
RxNorm for drugs, UCUM for units, and the Gender, Race, Ethnicity and Visit vocabularies). Keep the original
source values in the `*_source_value` columns. Use `concept_id = 0` only when there is genuinely no match, and
document it.

### 4.2 Deliverables

1. **Code:** your transformation module(s) and changes to `wrapper.py`, runnable with `docker compose up -d --build etl`.
2. **Mapping document:** for each source column, give the target table and field, the concept_id(s), and any rule
   or assumption. A Markdown file or spreadsheet is fine. See `docs/` for an example.
3. **Short write-up** (Markdown, max ~1 page) covering:
   - the key design decisions (e.g. how you avoid duplicate records and how you defined the observation period)
   - the data quality issues you found and how you handled them
   - the final row counts per OMOP table
   - what you would do differently with more time

---

## 5. How the ETL framework works

```
main.py ──► Wrapper.run()  (src/main/python/wrapper.py)
              ├─ drop + create CDM tables (public schema)
              ├─ create views on vocab.* (concept, domain, …) in public
              ├─ execute_transformation(fn)   ◄── your Python functions
              │     fn(wrapper) returns a list of ORM objects, which are bulk-inserted
              ├─ stem_table_to_domains()      ◄── SQL in src/main/python/post_processing/
              │     moves stem_table rows into measurement / condition_occurrence / drug_exposure /
              │     observation / procedure_occurrence / device_exposure / specimen
              └─ summary log
```

Important details:

- **Transformations** are plain functions `def my_transformation(wrapper) -> list:` that return ORM objects
  from `src/main/python/model/cdm/` (`Person`, `VisitOccurrence`, `ObservationPeriod`, `StemTable`, …).
  See `src/main/python/transformation/_skeleton.py` and the existing `basedata_*` / `fulong_*` files for examples.
  Register new functions in `src/main/python/transformation/__init__.py`.
- **`person`, `visit_occurrence` and `observation_period`** are written directly as ORM objects. Insert them
  **before** the stem table, because `stem_table.person_id` and `stem_table.visit_occurrence_id` are foreign keys.
- **The stem table routes rows by the domain of the concept.** Each post-processing SQL file joins
  `stem_table.concept_id` to `vocab.concept` and filters on `domain_id` (`'Measurement'`, `'Condition'`, `'Drug'`,
  `'Observation'`, `'Procedure'`, …). This means:
  - A stem row whose `concept_id` is not a concept in the expected domain ends up in the "wrong" table.
  - A stem row with `concept_id = 0` (or a concept_id that is not in your vocabulary) **silently disappears**.
    Always compare `stem_table` counts with the domain table counts.
  - Alternatively, you can write domain tables directly as ORM objects instead of going through the stem table.
    Either approach is fine; explain your choice.
- **`provider_id` and `care_site_id`** in OMOP are integer foreign keys to the `provider` and `care_site` tables.
  The source codes (`PR1`, `CS1`) cannot be inserted as-is. Either populate those tables, or leave the
  foreign keys empty and document why.
- **Existing mapping tables** in `resources/mapping_tables/` are PRIAS-specific. You may use the same approach
  (a CSV mapping file you read in code) or hard-code concept IDs in a dictionary. Either is acceptable, as long as it is clear and documented.
- **Finding concepts:** search in [Athena](https://athena.ohdsi.org/), or query the loaded vocabulary directly:
  ```sql
  SELECT concept_id, concept_name, domain_id, vocabulary_id, standard_concept
  FROM vocab.concept
  WHERE concept_name ILIKE '%hemoglobin%' AND vocabulary_id = 'LOINC' AND standard_concept = 'S';
  ```
  Remember to follow `Maps to` relationships in `vocab.concept_relationship` if you start from a non-standard concept.

### 5.1 Pointing the ETL at the challenge dataset

1. In `docker-compose.yml`, under the `etl` service, set:
   ```yaml
   - ETL_SOURCE=/app/resources/test_datasets/junior_challenge_30
   ```
2. In `src/main/python/wrapper.py`, in `run()`, **remove or comment out all the PRIAS transformations**
   (`basedata_*`, `fulong_*`, `enddata_*`, the `while self.has_next_fulong_batch()` loop and the episode steps), and
   call your own transformations instead. The PRIAS steps look for `basedata.csv`, `fulong.csv` and `enddata.csv`, and the
   `fulong` batch loop will crash the ETL when those files are missing.
3. Rebuild and run:
   ```bash
   docker compose up -d --build etl
   docker compose logs -f etl
   ```
   The ETL container has `restart: on-failure`. If your code crashes, it will keep restarting. Check the logs, fix the
   error, and rebuild.

Running locally instead of in Docker (with the `postgresql` container running):
```bash
pip install -r requirements.txt
python main.py -h localhost -p 5432 -d ohdsi -u admin -w secret -s resources/test_datasets/junior_challenge_30
```

### 5.2 Reference: what the PRIAS transformations do

- `basedata_to_person.py`: creates `person` records.
- `basedata_to_visit.py`, `fulong_to_visit.py`: create `visit_occurrence` records.
- `basedata_to_stem_table.py`, `fulong_to_stem_table.py`, `enddata_to_stem_table.py`: fill the intermediate
  `stem_table` using the mapping tables in `resources/mapping_tables/`.
- `basedata_to_observation_period.py`: creates `observation_period`.
- `post_processing/*.sql`: move rows from `stem_table` into the OMOP domain tables.

---

## 6. Verifying your results

Useful checks after a run:

```sql
-- Row counts per table
SELECT 'person' t, count(*) FROM public.person
UNION ALL SELECT 'observation_period', count(*) FROM public.observation_period
UNION ALL SELECT 'visit_occurrence', count(*) FROM public.visit_occurrence
UNION ALL SELECT 'stem_table', count(*) FROM public.stem_table
UNION ALL SELECT 'measurement', count(*) FROM public.measurement
UNION ALL SELECT 'condition_occurrence', count(*) FROM public.condition_occurrence
UNION ALL SELECT 'procedure_occurrence', count(*) FROM public.procedure_occurrence
UNION ALL SELECT 'drug_exposure', count(*) FROM public.drug_exposure
UNION ALL SELECT 'observation', count(*) FROM public.observation;

-- Records that could not be mapped to a standard concept
SELECT source_value, count(*) FROM public.stem_table WHERE concept_id = 0 GROUP BY 1;

-- Stem table rows that did not land in any domain table
SELECT s.concept_id, c.domain_id, count(*)
FROM public.stem_table s LEFT JOIN vocab.concept c USING (concept_id)
GROUP BY 1, 2 ORDER BY 3 DESC;
```

Sanity expectations:
- `person` = **15** and `visit_occurrence` = **30**
- Every clinical event has a date that falls within the patient's `observation_period`
- No events for a patient after their death date, unless you explicitly decide otherwise and document it
- Other counts depend on your design decisions (e.g. deduplication). Explain them in your write-up.

Optional: the OHDSI [Data Quality Dashboard](https://github.com/OHDSI/DataQualityDashboard) can be run with
`src/dqd/run_data_quality_assessment.R`.

---

## 7. How we evaluate

- **Correctness:** it runs end-to-end, and the records are complete and linked (person → visit → events).
- **Vocabulary mapping:** standard concepts are used where appropriate, source values are preserved, and units are mapped.
- **Data quality awareness:** issues are found, handled consistently and documented.
- **Code quality:** the code is readable, consistent with the existing framework, and has no hard-coded paths.
- **Communication:** the mapping document and write-up are clear.

Good luck!
