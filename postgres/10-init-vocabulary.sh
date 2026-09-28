#!/bin/bash

export PGPASSWORD=$POSTGRESQL_PASSWORD

echo "Starting OHDSI database initialization..."

# Check if vocabulary zip exists
if [ -f /vocab/vocabulary.zip ]; then
    echo "Unzipping vocabulary files..."
    unzip -o /vocab/vocabulary.zip -d /tmp/vocab/
    
    echo "Loading vocabulary into PostgreSQL..."
    psql -U $POSTGRESQL_USERNAME -d $POSTGRESQL_DATABASE << EOF

-- Create CDM schema
CREATE SCHEMA IF NOT EXISTS cdm;

-- Load each vocabulary table
\copy cdm.concept FROM '/tmp/vocab/CONCEPT.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.concept_relationship FROM '/tmp/vocab/CONCEPT_RELATIONSHIP.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.concept_ancestor FROM '/tmp/vocab/CONCEPT_ANCESTOR.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.concept_synonym FROM '/tmp/vocab/CONCEPT_SYNONYM.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.concept_class FROM '/tmp/vocab/CONCEPT_CLASS.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.domain FROM '/tmp/vocab/DOMAIN.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.relationship FROM '/tmp/vocab/RELATIONSHIP.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.vocabulary FROM '/tmp/vocab/VOCABULARY.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';
\copy cdm.concept FROM '/tmp/vocab/CONCEPT_CPT4.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b';

EOF

    echo "Vocabulary loading completed successfully!"
else
    echo "WARNING: vocabulary.zip not found in /vocab/ directory"
    echo "Database will start without vocabulary data"
fi