---
title: "SonarQube"
linkTitle: "SonarQube"
weight: 7
date: 2022-06-07
description: >  
---

# SonarQube

## Overview

[SonarQube®](http://www.sonarqube.org/) is an automatic code review tool to detect bugs, vulnerabilities and code smells in the code. It can integrate with the existing workflow to enable continuous code inspection across the project branches and pull requests.

We value high-quality engineering and look for ways to create high-quality production software.  So we need to have SonarQube checks as part of the CI pipeline to help ensure our code truly meets our [Definition of Done]({{< relref path="../Software Development Life Cycle/Definition Of Done/index.md" >}}).

The proposal of the DoD is that Unit Test Coverage should be >=80% on all new code as measured through SonarQube. Builds will fail when coverage is less than 80%

## SonarQube for Different Languages

SonarQube can perform analysis on up to 27 different languages. For our company the most used of them are:

- Clojure
- Python
- Java
- Javascript
- Typescript
- Kotlin

Specifics in the configuration for other languages described [here](https://sonarqube.tom.takeoff.com/documentation/analysis/languages/overview/).

### [Clojure](https://github.com/fsantiag/sonar-clojure)

#### Installation

Installation is not required, because we already have installed and configured sonarqube instance [here](https://sonarqube.tom.takeoff.com).

#### Usage

1. Change your project.clj file and add the required plugins:
   ```
   :plugins [[jonase/eastwood "0.3.6"]
            [lein-kibit "0.1.8"]
            [lein-ancient "0.6.15"]
            [lein-cloverage "1.1.2"]
            [lein-nvd "1.4.0"]]
    ```
    -Please make sure the plugins above are setup correctly for your project. A good way to test this is to execute each one of them individually on your project. Once they are running fine, SonarClojure should be able to parse their reports.

    -The lein plugin versions above are the ones we currently support. If you would like to test with a different version, keep in mind that it might cause errors on SonarClojure analysis.
2. Create a sonar-project.properties file in the root folder of your app:
    ```
    sonar.projectKey=your-project-key
    sonar.projectName=YourProjectName
    sonar.projectVersion=1.0
    sonar.sources=.
    ```
    The following keys will be necessary to run against our sonarqube:
    ```
    sonar.host.url=https://sonarqube.tom.takeoff.com
    sonar.login=<access_token>
    ```
3. Run [sonar-scanner](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner) on your project.

### [Python](https://docs.sonarqube.org/latest/analysis/languages/python/)

#### Language-Specific Properties
Discover and update the Python-specific [properties](https://sonarqube.tom.takeoff.com/documentation/analysis/analysis-parameters/) in: Administration > General Settings > Python.

#### Pylint

[Pylint](http://www.pylint.org/) is an external static source code analyzer, it can be used in conjunction with SonarPython.

You can enable Pylint rules directly in your Python Quality Profile. Their rule keys start with "Pylint:".

Once the rules are activated you should run Pylint and import its report:

`pylint <module_or_package> -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > <report_file>`

Then pass the generated report path to analysis via the `sonar.python.pylint.reportPath` property.

### [JAVA](https://docs.sonarqube.org/latest/analysis/languages/java/)

#### Language-Specific Properties

You can discover and update the Java-specific [properties](https://sonarqube.tom.takeoff.com/documentation/analysis/analysis-parameters/) in: Administration > General Settings > Java

#### Java Analysis and Bytecode

Compiled `.class` files are required for java projects with more than one java file. If not provided properly, the analysis will fail with the message:

`Your project contains .java files, please provide compiled classes with sonar.java.binaries property, or exclude them from the analysis with sonar.exclusions property.`

If only some `.class` files are missing, you'll see warnings like this:

`If only some .class files are missing, you'll see warnings like this:`

If you are not using Maven or Gradle for analysis, you must manually provide bytecode to the analysis. You can also analyze test code, and for that you need to provide tests binaires and test libraries properties.

| Key | Value |
| ----------- | ----------- |
| `sonar.java.binaries` (required) | Comma-separated paths to directories containing the compiled bytecode files corresponding to your source files. |
| `sonar.java.libraries` | Comma-separated paths to files with third-party libraries (JAR or Zip files) used by your project. Wildcards can be used: `sonar.java.libraries=path/to/Library.jar,directory/**/*.jar` |
| `sonar.java.test.binaries` | Comma-separated paths to directories containing the compiled bytecode files corresponding to your test files |
| `sonar.java.test.libraries` | Comma-separated paths to files with third-party libraries (JAR or Zip files) used by your tests. (For example, this should include the junit jar). Wildcards can be used: `sonar.java.test.libraries=directory/**/*.jar` |

### [JavaScript](https://docs.sonarqube.org/latest/analysis/languages/javascript/)

#### Prerequisites

In order to analyze JavaScript code, you need to have Node.js >= 8 installed on the machine running the scan. If the standard `node` is not available, you have to set property `sonar.nodejs.executable` to an absolute path to Node.js executable.

#### Language-Specific Properties

Discover and update the JavaScript-specific [properties](https://sonarqube.tom.takeoff.com/documentation/analysis/analysis-parameters/) in: **Administration > General Settings > JavaScript**

#### Supported Frameworks and Versions

-ECMAScript 5 / ECMAScript 2015 (ECMAScript 6) / ECMAScript 2016-2017-2018
-React JSX
-Vue.js
-Flow

### [Kotlin](https://docs.sonarqube.org/latest/analysis/languages/kotlin/)

#### Language-Specific Properties

You can discover and update Kotlin-specific [properties](https://sonarqube.tom.takeoff.com/documentation/analysis/analysis-parameters/) in: **Administration > General Settings > Kotlin**.

### [TypeScript](https://docs.sonarqube.org/latest/analysis/languages/typescript/)

#### Language-Specific Properties
Discover and update the TypeScript-specific [properties](https://sonarqube.tom.takeoff.com/documentation/analysis/analysis-parameters/) in: **Administration > General Settings > TypeScript**

#### Prerequisites

In order to analyze TypeScript code, you need to have Node.js >= 8 installed on the machine running the scan. If standard `node` is not available, you have to set property sonar.nodejs.executable to an absolute path to Node.js executable.

Also make sure to have [TypeScript](https://www.npmjs.com/package/typescript) as a project dependency or dev dependency. If it's not the case, add it:

```
cd <your-project-folder>
npm install -D typescript
```

If you can't have TypeScript as a project dependency you can set your `NODE_PATH` variable to point to your globally installed TypeScript (but this is generally discouraged by the Node.js documentation).

### [Go](https://docs.sonarqube.org/latest/analysis/languages/go/)

#### Language-Specific Properties
You can discover and update the Java-specific [properties](https://sonarqube.tom.takeoff.com/documentation/analysis/analysis-parameters/) in: Administration > General Settings > Go

#### "sonar-project.properties" Sample
Here is a first version of a sonar-project.properties file, valid for a simple Go project:
   ```
  sonar.projectKey=com.company.projectkey1
  sonar.projectName=My Project Name

  sonar.sources=.
  sonar.exclusions=**/*_test.go

  sonar.tests=.
  sonar.test.inclusions=**/*_test.go
   ```

## SonarScanner for Azure DevOps

TODO: Is this still supported? Does this need to be converted to GitHub Actions?

## Related Pages

- [Takeoff SonarQube Projects](https://sonarqube.tom.takeoff.com/projects)   
- [SonarQube Documentation](https://docs.sonarqube.org/latest/)   
- [Languages: Overview](https://docs.sonarqube.org/latest/analysis/languages/overview/)   
- [Importing External Issues](https://sonarqube.tom.takeoff.com/documentation/analysis/external-issues/)   
- [Test Coverage & Execution](https://sonarqube.tom.takeoff.com/documentation/analysis/coverage/)   
