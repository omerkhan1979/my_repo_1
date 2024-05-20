#!/bin/bash

# path to auto-generated doc file
FILE_PATH="env_setup_tool/ENV_SETUP.md"
# Save the current PYTHONPATH
ORIGINAL_PYTHONPATH=$PYTHONPATH

REPO_ROOT=$(pwd)
export PYTHONPATH=$REPO_ROOT:$PYTHONPATH

#typer doc auto-generation
typer env_setup_tool.src.env_setup utils docs --name env-setup-tool --output $FILE_PATH

# at the moment the tool runs as a python module, using `python -m <module_path>`
# to reflect this usage the below script updates the typer doc auto-generation from `env-setup-tool` to `python -m env_setup_tool.src.env_setup`
if [ -f "$FILE_PATH" ]; then
  sed -i'.bak' -e 's/\$ env-setup-tool/\$ python -m env_setup_tool.src.env_setup/g' "$FILE_PATH"
  echo "command updated in $FILE_PATH"
  rm -f "${FILE_PATH}.bak"
else
  echo "File not found: $FILE_PATH"
fi

# Revert PYTHONPATH
export PYTHONPATH=$ORIGINAL_PYTHONPATH
