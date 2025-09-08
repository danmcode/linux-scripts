#!/bin/bash
# Bareos Volume Cleanup Script - Professional Edition

STATUS_TO_DELETE="Error"
LOG_FILE="/var/log/bareos/volume_cleanup.log"
DRY_RUN=false  # set to true for testing

# Check for bconsole
command -v bconsole >/dev/null 2>&1 || { echo "bconsole not found! Exiting."; exit 1; }

# Fetch volume list
VOLUMES=$(bconsole << EOF
list volumes
EOF
)

# Extract only volumes with Error status
ERROR_VOLUMES=$(echo "$VOLUMES" | awk -v status="$STATUS_TO_DELETE" '$0 ~ status {print $4}')

# Exit if none found
if [ -z "$ERROR_VOLUMES" ]; then
  echo "No volumes with status '$STATUS_TO_DELETE' found."
  exit 0
fi

# Process each volume
for volname in $ERROR_VOLUMES; do
  if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Would delete volume: $volname"
  else
    echo "Deleting volume $volname..."
    echo "$(date) - Deleting volume $volname" >> "$LOG_FILE"
    bconsole << EOF
delete volume=$volname yes
EOF
  fi
done
