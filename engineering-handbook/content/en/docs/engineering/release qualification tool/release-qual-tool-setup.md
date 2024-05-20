---
title: "Release qualification tool setup"
linkTitle: "Release qual tool setup"
weight: 1
description: >-
    How to install release qualification tool
---

1. First of all you need to clone the [Release qualification tool](https://github.com/takeoff-com/python_tests) to your local machine
2. To use service tokens and launchdarkly keys, `shared-tokens` are connected to the project as git submodule.

You need to initialize git submodule:

```bash
git submodule init

git submodule update
```
3. Resolve dependencies:
   [Poetry](https://python-poetry.org) is using for dependecy management.
* To install poetry, please execute:
```bash
pip3 install poetry
```
* To create and activate the virtual environment, and install the dependencies from `poetry.lock` execute:
```bash
poetry shell
poetry install
```
* In case you introduce new dependency, please add it to `pyproject.toml` and `poetry.lock` :
```
poertry add <package>
```
* If you need to update versions of libraries/packages in .lock file to the latest, execute:
```bash
poetry update
```
**Now you are ready to start using it.**