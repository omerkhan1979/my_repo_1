#!/bin/bash

# Kill the currently running server
echo "Killing server"
adb kill-server
# List all the attached devices
adb devices -l
# Kill all attached emulators
adb devices | grep emulator | cut -f1 | while read line; do adb -s $line emu kill; done
# Restart the server
echo "Starting server"
adb start-server
