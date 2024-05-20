---
title: "GITHUB ENV for GitHub Actions"
linkTitle: "GitHub Actions Environment"
weight: 5
date: 2022-09-30
description: >  
---
# GITHUB ENV reference examples


> **Note**   
> We left concrete examples of `GITHUB ENV` for **GitHub Actions** here, as we can’t really find this in the _GH documentation_.


## PUSH  

```
echo ${GITHUB_REF} -> refs/heads/release/PROD-0000
echo ${GITHUB_HEAD_REF} -> <BLANK>
echo ${GITHUB_REF_NAME} -> release/PROD-0000
```


## PULLREQUEST

```
echo ${GITHUB_REF} -> refs/pull/4/merge
echo ${GITHUB_REF/refs/pull//} -> 4/merge
echo ${GITHUB_HEAD_REF} -> release/PROD-000
echo ${GITHUB_REF_NAME} -> 4/merge
```

## Referencing Default GitHub Environment Variables  

The default environment variables that GitHub sets are available to every step in a [workflow](https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables).

`GITHUB_JOB` – Provides **job_id** of the current job.  
`GITHUB_ACTION` – Provides the **id** of the current action.  
`GITHUB_ACTION_PATH` – Provides the path where your action is located.  
`GITHUB_ACTOR` – provides the **name** of the _person_ or _app_ that initiated the workflow, like your GitHub username.  
`GITHUB_RUN_ID` – provides the unique number of the `run` command.  
