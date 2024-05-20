#!/usr/bin/env bash

branch_prefix_re="feature|release|hotfix|bugfix"
jira_key_re="[A-Z]{2,8}-[0-9]{1,8}"

# Echoes the current git branch.
function get_current_branch() {
  # There is no branch name in a detached HEAD state, such as during interactive
  # rebase.
  branch_name=$(git symbolic-ref --short HEAD 2>&1)
  ref_error="$?"

  if [[ $ref_error -eq "0" && -n $branch_name ]]; then
    echo "$branch_name"
  fi
}

# Echoes the Jira key portion of a branch.
# get_jira_key_from_branch <branch-name>
function get_jira_key_from_branch() {
  local branch_name="$1"

  local sub_match=$(echo "$branch_name" | grep -Eo "^($branch_prefix_re)/$jira_key_re")

  if [[ -n $sub_match ]]; then
    echo "$sub_match" | grep -Eo "$jira_key_re"
  fi
}

# Makes a regex string that matches the required portion of a commit message.
# make_commit_message_jira_re <jira-key>
function make_commit_message_jira_re() {
  local jira_key="$1"
  echo "^$jira_key: "
}
