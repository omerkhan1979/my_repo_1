Pytest Behavior-Driven Development Testing Framework
==
[[Table of Contents](../README.md#table-of-contents)]

## Introduction
[Behavior-Driven Development (BDD)](https://en.wikipedia.org/wiki/behavior-driven_development) is a collaborative software development approach that emphasizes clear communication between developers, testers, and business stakeholders. It focuses on creating human-readable scenarios that serve as both requirements and definitions for features, facilitating a shared understanding and alignment on project goals.

The [Pytest BDD Testing Framework](https://pytest-bdd.readthedocs.io/en/stable/) is a powerful tool for implementing BDD principles when writing tests for our software products. 

## Framework Overview 

This section provides an overview of the main components of the Framework, how to set up your environment, and other setup and usage details.

For information about BDD Workflow Guidance and .feature file writing, see the [Engineering Handbook](https://engineering-handbook.takeofftech.org/docs/engineering/behavior-driven-development/_index.md). 

- [Pytest Behavior-Driven Development Testing Framework](#pytest-behavior-driven-development-testing-framework)
  - [Introduction](#introduction)
  - [Framework Overview](#framework-overview)
      - [Components Overview Diagram](#components-overview-diagram)
    - [Directory Structure](#directory-structure)
  - [Environment Setup](#environment-setup)
      - [Prerequisites](#prerequisites)
      - [Installation](#installation)
      - [Configuration](#configuration)
      - [Usage](#usage)
      - [Test Execution](#test-execution)
      - [Environment Configuration Tool](#environment-configuration-tool)
- [Example command to run a test](#example-command-to-run-a-test)

#### Components Overview Diagram
The following diagram outlines how the components of the Framework interact with the Pytest BDD framework and Environment Setup tool.

<br />
<div align="center">
  <a href="https://github.com/takeoff-com/release-qualification-tools">
    <img src="/pytest_BDD/docs/images/bdd_diagram.png" alt="BDD Framework" height=auto max-width=auto>
  </a>
</div>

### Directory Structure

To support the BDD Testing Framework, in this repo the `/tests` directory now contains the `features/` and `step_defs/` subdirectories under which all `.feature` and Step Definition files are stored. All common Step Definitions must be added to the `conftest.py` file which is located in the `step_defs/` folder.

```bash
bdd-gherkin-test-automation-framework/
├─ .github/
│  ├─ workflows/
│  │  ├─ ci.yml
├─ tests/
│  ├─ features/
│  │  ├─ sample.feature
│  ├─ step_defs/
│  │  ├─ conftest.py
│  │  ├─ test_sample.py
│  ├─ .env
│  ├─ .gitignore
│  ├─ conftest.py
│  ├─ pytest.ini

```
**Utils**
All definitions of the APIs that are required in validations of test steps use the existing utils structure for the feature framework.

## Environment Setup
Follow these steps to set up your environment so that you can create BDD tests.

#### Prerequisites
⚠️ **Please note**: `Python 3.10` or newer is required.

The [Pycharm](https://www.jetbrains.com/pycharm/) IDE offers a [BDD Testing Framework](https://www.jetbrains.com/help/pycharm/bdd-frameworks.html) that allows you to create, manage, and run `.feature` files and Step Definitions. We strongly recommend using Pycharm to create and run tests.

#### Installation

Use your preferred package manager to install the BDD Framework. For example, using `pip`:

```bash
$ pip install --upgrade pip
$ pip install pytest-bdd
```

#### Configuration
Configure the BDD Framework Name by creating a configuration file in your project directory.
<!--I believe @satya said poetry has some libraries and we are not actually using config files. He is going to add some info about that. -->

#### Usage
With BDD Framework, you can write BDD tests that are both powerful and easy to understand.

#### Test Execution
BDD tests can be executed using BDD Framework Name's CLI:
```bash
# Example command to run a test
poetry run pytest -m test_marker -v -s 
```

### Environment Configuration Tool

Currently, we use the `run_env_setup_tool` function in [cmd_line.py](https://github.com/takeoff-com/release-qualification-tools/blob/master/src/utils/cmd_line.py) to call out to the [env_setup_tool](https://github.com/takeoff-com/release-qualification-tools/tree/master/env_setup_tool) and apply features.  If you need to pass options to the `env_setup_tool`, you can do so by setting the `BDD_CMD_LINE_OPTIONS` environment variable with your options.

```bash
export BDD_CMD_LINE_OPTIONS="--branch=feature/PROD-0000 --location=0068"
poetry run pytest -m test_marker -v -s 
```

Reasons you might do this:
 - Testing a new or modified environment-config definition (feature)
   - Test your new/updated feature by setting the branch option (`--branch=feature/myBranchName`) to your [environment-configs](https://github.com/takeoff-com/environment-configs) branch, then running your BDD test(s)
 - Passing in an MFC location (defaults to 9999)

