#!/bin/bash
set -e
DB_NAME=$1
PROJECT_ID=$2
REGION=$3
SOURCE_DB_IP=$4
CLOUD_SQL_INSTANCE_ID=$5
USER_SECRET=$6
PASS_SECRET=$7
if [ -z "$DB_NAME" ]; then echo "Missing DB_NAME"; exit 1; fi
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
SOURCE_PROFILE_NAME="source-profile-${DB_NAME}-${TIMESTAMP}"
DEST_PROFILE_NAME="dest-profile-${DB_NAME}-${TIMESTAMP}"
MIGRATION_JOB_NAME="mig-job-${DB_NAME}-${TIMESTAMP}"
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

# --- MONITORING LOOP ---
echo "Monitoring migration job status... This may take a while."
while true; do
    STATUS=$(gcloud database-migration migration-jobs describe "${MIGRATION_JOB_NAME}" --region="${REGION}" --project="${PROJECT_ID}" --format="value(phase)")
    echo "Current job phase: '${STATUS}'"

    if [ "${STATUS}" == "COMPLETED" ]; then
        echo "Migration job completed successfully."
        break
    elif [[ "${STATUS}" == "FAILED" || "$STATUS" == "STOPPED" ]]; then
        echo "Migration job failed or was stopped. Please check the GCP console for details."
        exit 1
    fi
    sleep 30 # Wait for 30 seconds before checking again
done

echo "DMS workflow completed for $DB_NAME."