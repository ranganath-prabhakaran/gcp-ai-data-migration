#!/bin/bash
set -e
DB_NAME=$1
PROJECT_ID=$2
REGION=$3
SOURCE_DB_IP=$4
CLOUD_SQL_INSTANCE_ID=$5
if [ -z "$DB_NAME" ]; then echo "Missing DB_NAME"; exit 1; fi
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
SOURCE_PROFILE_NAME="source-profile-${DB_NAME}-${TIMESTAMP}"
DEST_PROFILE_NAME="dest-profile-${DB_NAME}-${TIMESTAMP}"
MIGRATION_JOB_NAME="mig-job-${DB_NAME}-${TIMESTAMP}"
USER_SECRET="source-db-user"
PASS_SECRET="source-db-password"
echo "-> Starting DMS Workflow for '${DB_NAME}'..."
echo "   1. Creating Source Connection Profile..."
gcloud database-migration connection-profiles create "${SOURCE_PROFILE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --provider=mysql --hostname="${SOURCE_DB_IP}" --username-secret-id="${USER_SECRET}" --password-secret-id="${PASS_SECRET}" --quiet
echo "   2. Creating Destination Connection Profile..."
gcloud database-migration connection-profiles create "${DEST_PROFILE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --provider=cloudsql --cloudsql-instance-id="${CLOUD_SQL_INSTANCE_ID}" --quiet
echo "   3. Creating Migration Job..."
gcloud database-migration migration-jobs create "${MIGRATION_JOB_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --source="${SOURCE_PROFILE_NAME}" --destination="${DEST_PROFILE_NAME}" --type=ONE_TIME --quiet
echo "   4. Starting Migration Job..."
gcloud database-migration migration-jobs start "${MIGRATION_JOB_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --quiet
echo "-> DMS Workflow for '${DB_NAME}' initiated."
