#!/bin/bash

# Specify the path to your .env file
ENV_FILE=".env.prod"

# Check if the .env file exists
if [[ ! -f $ENV_FILE ]]; then
  echo "Error: $ENV_FILE file not found!"
  exit 1
fi

# Read the .env file and construct the eb setenv command
eb_setenv_command="eb setenv"

while IFS='=' read -r key value; do
  # Ignore comments and empty lines
  [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
  eb_setenv_command+=" $key=$value"
done < "$ENV_FILE"

# Output the command for verification (optional)
echo "$eb_setenv_command"