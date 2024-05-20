---
title: "Code Style"
linkTitle: "Code Style"
weight: 7
date: 2022-06-21
description: >  
---

## Overview 
Code style is a document that gives coding conventions, comprising the standard library in the main programming language distribution. The style guide evolves over time as additional conventions are identified and past conventions are rendered obsolete by changes in the language itself.

Many projects have their own coding style guidelines. In the event of any conflicts, such project-specific guides take precedence for that project. Anyway, this page should help in the process of Engineering [Onboarding]({{< relref path="../../Onboarding/newcomers_onboarding.md" >}}) to raise the competency, why we need code style guidelines, and what type of guides and tools we'll use in our stack of technologies.    

A style guide is about consistency. Consistency with the style guide is important. Consistency within a project is more important. Consistency within one module or function is the most important.

## Conventions and style guides

### Python[^1]   

   - Code Layout
      - Indentation
      - Tabs or Spaces
      - Maximum Line Length
      - Line Break
      - Blank Lines
      - Source File Encoding
      - Imports
      - Module Level Names
   - String Quotes
   - Whitespace in Expressions and Statements
   - Trailing Commas
   - Comments
      - Block Comments
      - Inline Comments
      - Documentation Strings
   - Naming Conventions
      - Overriding Principle
      - Descriptive: Naming Styles
      - Prescriptive: Naming Conventions
         - Package and Module Names
         - Class Names
         - Type Variable Names
         - Exception Names
         - Global Variable Names
         - Function and Variable Names
         - Method Names and Instance Variables
         - Constants
         - Inheritance
      - Public and Internal Interfaces
   - Programming Recommendations
      - Function and Variable Annotations   


### Go[^2]

   - Formatting
   - Commentary
   - Names
      - Package names
      - Getters
      - Interface names
      - MixedCaps
   - Semicolons
   - Control structures 
      - Redeclaration and reassignment
      - If / For / Switch / Type switch
   - Functions
      - Multiple return values
      - Named result parameters
      - Defer
   - Data
      - Allocation with new / make
      - Constructors and composite literals
      - Arrays / Slices / Two-dimensional slices / Maps / Printing / Append
   - Initialization
      - Constants/Variables/The init function
   - Methods
      - Pointers vs. Values
   - Interfaces and other types
      - Interfaces
      - Conversions
      - Interface conversions and type assertions
      - Generality
      - Interfaces and methods
   - The blank identifier
      - The blank identifier in multiple assignment
      - Unused imports and variables
      - Import for side effect
      - Interface checks
   - Embedding
   - Concurrency
      - Share by communicating
      - Goroutines
      - Channels
      - Channels of channels
      - Parallelization
      - A leaky buffer
   - Errors
      - Panic
      - Recover 
   - A web server

## Tools

### IDE 

#### GoLand[^3]

GoLand lets you reformat your code according to the requirements you've specified in your current code style scheme or the `.editorconfig` file. If anything is not defined in .editorconfig, it's taken from the project settings.

You can reformat a part of code, the whole file, group of files, a directory, and a module. You can also exclude part of code or some files from the reformatting.

#### Visual Studio[^4] [^5] 

You can define code style settings per-project by using an _EditorConfig file_, or for all code you edit in Visual Studio on the text editor _Options page_ on Windows. **Editor behaviors** can be set to allow code to be formatted as it's written. These actions are set under `Visual Studio > Preferences > Text Editor > Behavior`, and some of the more commonly used functions could be met there. 


#### PyCharm[^5]

If certain coding guidelines exist in a company, one has to follow these guidelines when creating source code. PyCharm helps you maintain the required code style.

The IDE comes with two pre-defined schemes: the **Project** scheme and the **Default** scheme.

### Static analysis | [SonarQube]({{< relref path="./sonarqube.md" >}})   

With SonarQube static analysis you'll have one place to measure the Reliability, Security, and Maintainability of all the languages in your project, and all the projects in your sphere. They have made and continue to make serious investments in their analyzers to keep value up and false positives down.

From language to language they give to users a cohesive experience and a consistent set of metrics as well as hundreds of static code analysis rules.   


### GitHub Actions and CLI tools as part of CI/CD Pipeline

#### PyBlack[^7] 
Create a file named `.github/workflows/black.yml` inside your [repository](https://github.com/takeoff-com/poc-templated-cicd-python/blob/master/.github/workflows/black.yaml) with:  

```
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: psf/black@stable
```

#### Flake8[^8]

Flake8 can be included as a hook for pre-commit. The easiest way to get started is to add this configuration to your `.pre-commit-config.yaml`:

```
-   repo: https://github.com/pycqa/flake8
    rev: ''  # pick a git hash / tag to point to
    hooks:
    -   id: flake8
```

Once you have installed **Flake8** we can specify command-line options directly, it’s also possible to narrow that **Flake8** will try to check by specifying exactly the paths and directories you want it to check. Let’s assume that we have a directory with python files and sub-directories which have python files (and may have more sub-directories) called `my_project`. Then if we only want errors from files found inside `my_project` we can do:  

```
$ flake8 my_project
```   

#### Golang lint[^9]

`golangci-lint` is a fast Go linters runner. It runs linters in parallel, uses caching, supports `.yaml` config, has integrations with all major IDE and has dozens of linters included.

Add `.github/workflows/golangci-lint.yml` with the following contents:

```
name: golangci-lint
on:
  push:
    branches:
      - master
      - main
  pull_request:
permissions:
  contents: read
  # Optional: allow read access to pull request. Use with `only-new-issues` option.
  # pull-requests: read
jobs:
  golangci:
    name: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-go@v3
        with:
          go-version: 1.17
      - uses: actions/checkout@v3
      - name: golangci-lint
        uses: golangci/golangci-lint-action@v3
        with:
          # Optional: version of golangci-lint to use in form of v1.2 or v1.2.3 or `latest` to use the latest version
          version: v1.29
```


[^1]: [Style Guide for Python Code](https://peps.python.org/pep-0008/)  
[^2]: [Effective Go](https://go.dev/doc/effective_go)  
[^3]: [GoLand IDE](https://www.jetbrains.com/help/go/reformat-and-rearrange-code.html#configure-leading-spaces-in-comments)  
[^4]: [Visual Studio Code style preferences](https://docs.microsoft.com/en-us/visualstudio/ide/code-styles-and-code-cleanup?view=vs-2022)  
[^5]: [Visual Studio Editor Behavior](https://docs.microsoft.com/en-us/visualstudio/mac/editor-behavior?view=vsmac-2022)  
[^6]: [PyCharm Configuring code style](https://www.jetbrains.com/help/pycharm/configuring-code-style.html)  
[^7]: [Python Black](https://black.readthedocs.io/en/stable/integrations/github_actions.html)  
[^8]: [Flake8: Tool For Style Guide Enforcement](https://flake8.pycqa.org/en/latest/user/invocation.html)  
[^9]: [Go linters aggregator](https://github.com/golangci/golangci-lint-action)  
