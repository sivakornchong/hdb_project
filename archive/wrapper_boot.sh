#!/usr/bin/bash

# Log file path
LOG_FILE=~/log_file.txt

# Function to log timestamps
log_timestamp() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Log start time
log_timestamp "Wrapper script started"

# Run the first command
log_timestamp "Executing boot.sh"
bash ~/hdb_project/boot.sh

# Run the second command
log_timestamp "Executing huggingface_boot.sh"
bash ~/HDB_resale_predict/huggingface_boot.sh

# Log end time
log_timestamp "Wrapper script completed"

# Shut down the VM
# log_timestamp "Shutting down the VM"
# sudo shutdown -h now

