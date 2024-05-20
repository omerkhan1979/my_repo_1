---
title: "Unit Tests Metrics"
linkTitle: "Unit Tests Metrics"
weight: 7
date: 2022-06-09
description: >  
---
## Unit Tests Metrics
Continuous Integration and Continuous Delivery in an Agile driven project environment is meaningless without Continuous Testing. The ability to measure progress of a continuous testing process at each stage of the application delivery life cycle is vital to launch quality software with minimal business risks. Do not mix meterics for Unit Tests and [Static Analysis](content/en/docs/Engineering/Continuous integration and Deployment/static-analysis.md).   

### Metrics

1. **Code coverage %**   
   Code coverage is performed to verify the extent to which the code has been executed. Code coverage tools use static instrumentation in which statements monitoring code execution are inserted at necessary junctures in the code. Code coverage scripts generate a report that details how much of the application code has been executed. This is a white-box testing technique.   
   ![code coverage](/images/en/docs/Engineering/cicd/unit-metric-1.png)

2. **Cyclomatic complexity**  
   Cyclomatic complexity of a code section is the quantitative measure of the number of linearly independent paths in it. It is a software metric used to indicate the complexity of a program. It is computed using the Control Flow Graph of the program.      
   ![cyclomatic complexity](/images/en/docs/Engineering/cicd/unit-metric-2.png)   
   `E` = _Number of edges_ `N` = _Number of nodes_

3. **Test Pass % rate**
   Passing rate, in general, can be characterized as a test metric, and may be presented as a measure of success. The pass rate of a test is `P = (p ÷ t) × 100`, where `P` is the pass rate, `p` is the number of passed test cases/unit tests that passed the test, and `t` is the total number of test cases/unit tests that were executed or took part in the test run.   
   ![pass rate](/images/en/docs/Engineering/cicd/unit-metric-3.png)

4. **Build Quality**   
   This is one another metric to measure Build Quality is more specific, and means how well was it put together. In general it count the rate of successfully passed builds vs. all build pushes.  
   ![build quality](/images/en/docs/Engineering/cicd/unit-metric-4.png)


### Examples

#### [Coverage](https://coverage.readthedocs.io/en/6.4.1/)   
Coverage measurement is typically used to gauge the effectiveness of tests. It can show which parts of your code are being exercised by tests, and which are not.
It monitors your program, noting which parts of the code have been executed, then analyzes the source to identify code that could have been executed but was not.

```
$ coverage report -m
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
my_program.py                20      4    80%   33-35, 39
my_other_module.py           56      6    89%   17-23
-------------------------------------------------------
TOTAL                        76     10    87%
```   
#### [Codecov](https://about.codecov.io/blog/getting-started-with-code-coverage-for-golang/)   
![codecov report](/images/en/docs/Engineering/cicd/unit-coverage-1.jpg)

#### [GoConvey](http://goconvey.co/)
![goconvey](/images/en/docs/Engineering/cicd/unit-coverage-2.png)

#### [Clojure.test](https://clojure.github.io/clojure/clojure.test-api.html)
A unit testing framework based on the core of the library is the "is" macro, which lets you make assertions of any arbitrary expression.   
