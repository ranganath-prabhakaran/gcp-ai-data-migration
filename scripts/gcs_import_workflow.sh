#!/bin/bash
set -e
DB_NAME=$1
GCS_BUCKET=$2
CLOUD_SQL_INSTANCE=$3
GCP_PROJECT_ID=$4
if [ -z "$DB_NAME" ]; then echo "Missing DB_NAME"; exit 1; fi
if [ -z "$SOURCE_DB_USER" ]; then echo "Missing SOURCE_DB_USER env var"; exit 1; fi
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
DUMP_FILENAME="${DB_NAME}-${TIMESTAMP}.sql.gz"
LOCAL_DUMP_PATH="/tmp/${DUMP_FILENAME}"
GCS_URI="gs://${GCS_BUCKET}/${DUMP_FILENAME}"
echo "-> Starting GCS Import Workflow for '${DB_NAME}'..."
echo "   1. Dumping and compressing database..."
mysqldump --host="${SOURCE_DB_HOST}" --user="${SOURCE_DB_USER}" --password="${SOURCE_DB_PASSWORD}" --single-transaction --routines --triggers --source-data=2 --databases "${DB_NAME}" | gzip > "${LOCAL_DUMP_PATH}"
echo "   2. Uploading dump to ${GCS_URI}..."
gsutil cp "${LOCAL_DUMP_PATH}" "${GCS_URI}"
echo "   3. Importing into Cloud SQL instance '${CLOUD_SQL_INSTANCE}'..."
gcloud sql import sql "${CLOUD_SQL_INSTANCE}" "${GCS_URI}" --database="${DB_NAME}" --project="${GCP_PROJECT_ID}" --quiet
echo "   4. Cleaning up local file..."
rm "${LOCAL_DUMP_PATH}"
echo "-> GCS Import Workflow finished."
