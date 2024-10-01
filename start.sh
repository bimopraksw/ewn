#!/bin/bash

# Path to the API keys file
API_KEYS_FILE="api.txt"

# Path to the Python script
PYTHON_SCRIPT="script.py"

# Check if the API keys file exists
if [ ! -f "$API_KEYS_FILE" ]; then
  echo "API keys file not found!"
  exit 1
fi

# Initialize a counter for log file names
counter=1

# Loop through each line in the API keys file
while IFS= read -r api_key; do
  if [ -n "$api_key" ]; then
    log_file="${counter}.log"
    echo "Starting Python script with API key: $api_key (log: $log_file)"
    
    # Run the Python script and redirect output to the corresponding log file
    python3 "$PYTHON_SCRIPT" "$api_key" > "$log_file" 2>&1 &
    
    # Increment the counter for the next log file
    ((counter++))
  fi
done < "$API_KEYS_FILE"

# Wait for all background processes to finish
wait
echo "All Python scripts have finished running."
