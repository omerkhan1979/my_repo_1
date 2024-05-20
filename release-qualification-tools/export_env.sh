#!/bin/bash

#Command to execute: "source ./export_env.sh /..Path of../garden.global.yaml"

current_dir=$(dirname "$0")

# Get the path to the gardenfile.yaml as the second parameter
gardenfile_path="$1"

# Check if the parameter is provided
if [ -z "$gardenfile_path" ]; then
  echo "Error: Please provide the path to the garden_file script."
  echo "Usage: $0 <path_to_python_script>"
  exit 1
fi
# Run the Python script to get the environment variables
# Replace "/path/to/python" with the path to your Python executable
# Replace "/path/to/get_env_vars.py" with the actual path to the Python script
chmod +x "$current_dir/tests/test_envsetup.py"
env_vars=$("$current_dir/tests/test_envsetup.py")

# Export the environment variables in the current shell
eval "$env_vars"