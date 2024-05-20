Testrail Reporting
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](../../getting-started/00-getting-started.md)

Sending results to Testrail is a relatively straightforward process that uses the [Testrail API](https://support.testrail.com/hc/en-us/articles/7077083596436-Introduction-to-the-TestRail-API) and [pytest-testrail](https://pypi.org/project/pytest-testrail/).

- [Testrail Reporting](#testrail-reporting)
    - [Setup](#setup)
    - [Reporting](#reporting)
    - [Github Workflow](#github-workflow)


### Setup

To report the RQ results into testrail, you need a Testrail API Key. 
1. Log in to Testrail and at the upper right, click **[yourname]** > **settings** > **api keys** > **add key**
2. Add a **name** > **generate key** > *save your key somewhere so you dont lose it* > **add key** > **SAVE SETTINGS** -- dont miss this last click.
3. You will need to set two environment variables in your execution session/terminal
    ```
    export TESTRAIL_EMAIL=<fname.lname>@takeoff.com
    export TESTRAIL_API_KEY=<key-generated-in-above-step>
    ```

Additionally, you need the Run ID from the url of the Test Run, for example, if your Test Run is https://takeofftech.testrail.io/index.php?/runs/view/7146, then the Run ID is 7146.


### Reporting

- `trcli` is used to send results to TestRail, see example below.  
- Include `--tr-skip-missing` so that the skipped tests don't count against the total % passed.
- Add either `--tr-testrun-name` OR `--tr-run-id` OR `--tr-plan-id`
If more than one of the above is provided, the `tr-run-id` recieves priority over `--tr-plan-id`.

If, for example, you want to run the full ```rq``` suite and report the results to an existing Test Run for a Release Train, you would use the following commands:

```sh
pytest -v -s -m rq --l [location] --junitxml=[/path/to/your/dir]/results.xml

poetry run python3 utils/filter_xunit_file.py --result-xml results.xml

poetry run trcli -h https://takeofftech.testrail.io --project Product --project-id 3 --username $TESTRAIL_EMAIL --key $TESTRAIL_API_KEY --no parse_junit --case-matcher "property" --run-id [run id] --title ["required but can be any title"] --file [/path/to/your/dir]/results.xml
```

If you recieve an error message that a particular case id isnt found, you can open results.xml, find the caseid, and remove the particular tag that includes it, then re-try the final trcli command.

For more information see: [pytest-testrail](https://pypi.org/project/pytest-testrail/)

### Github Workflow

The [Deploy to ODE](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to-ode.yaml) github workflow can also be used to report to testrail, but is primarily designed for Release Train testing and reporting. You must select a Release Train version, and the workflow creates a new Test Plan and Test Run each time. 

For more information, see the [Release Train Management](https://github.com/takeoff-com/release-train-management/blob/master/docs/how-to/04-deploy-an-ode.md) repo documentation.
