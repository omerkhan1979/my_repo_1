Allure Reporting
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Start](../../getting-started/00-getting-started.md)

Allure Reports are an open-source tool we use to better visualize test results.

To generate an Allure report, add a path to the directory where test report data is collected (```--alluredir=./<directory>```):

```sh
pytest -v -s -m smoke --r <retailer> --e <env> --l <location-code-tom> --alluredir=./test-report
```


To serve a test report use command ```allure serve <directory>```:    ```allure serve test-report ```