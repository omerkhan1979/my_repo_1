#!/usr/bin/env bash
HOOK_NAMES="pre-commit commit-msg post-checkout prepare-commit-msg pre-push"
# assuming the script is in a bin directory, one level into the repo
HOOK_DIR=$(git rev-parse --show-toplevel)/.git/hooks

for hook in $HOOK_NAMES; do
    # If the hook already exists, is executable, and is not a symlink
    if [ ! -h $HOOK_DIR/$hook -a -x $HOOK_DIR/$hook ]; then
        # move hook to hook.local
        mv $HOOK_DIR/$hook $HOOK_DIR/$hook.local
    fi
    # create the symlink, overwriting the file if it exists
    ln -s -f ../../takeoff-utils/githooks/hooks-wrapper $HOOK_DIR/$hook
    chmod +x $HOOK_DIR/$hook

done

OTHERS="helpers.sh"

for other in $OTHERS; do
    if [[ ! -h $HOOK_DIR/$other && -e $HOOK_DIR/$other ]]; then
      mv $HOOK_DIR/$other $HOOK_DIR/$other.local
    fi

    ln -s -f ../../takeoff-utils/githooks/$other $HOOK_DIR/$other
done
