---
title: "CI/CD Internal Examples"
linkTitle: "CI/CD Internal Examples"
weight: 7
date: 2022-07-22
description: >
---

## CI Internal Examples

### Karate BDD Tests

[Karate](https://github.com/karatelabs/karate) is the only open-source tool to combine API test-automation, mocks, performance-testing and even UI automation into a single, unified framework with BDD syntax.

The integration should meet several conditions to run:

 1. Pull a correct Docker image with Karate infrastructure configured. *(July 22, 2022) end-to-end functionality available only for the Inbound tests suite at this point.*
 1. Pull Karate tests from your repository – this step is optional for most Inbound teams
 1. Run tests and generate Karate report in JSON format for respective environments
 1. Run the automation reporting tool to register the result of your test run in JIRA


 Here is the pseudo-code [Github Actions](https://docs.github.com/en/actions) YAML pipeline configuration:

```go {.myclass linenos=table}

karateTests:
  name: Integration tests execution (Karate)
  runs-on: ubuntu-latest
  # Here are deployment pre-conditions:
  # so you're making sure your service deployed before test run
  needs: [deployToTestEnv, ... ] 
  container:
      # this is temporary: we'll abstract out into generic container
      image: gcr.io/takeoff-204116/inbound-integration-tests:latest
      env:
        APP_PATH: ../../../usr/src/app
      credentials:
        username: _json_key
        password: ${{ secrets.GCR_LOGIN }}
  steps:
      # EXAMPLE: here we're running Karate tests 
      # for Decanting Service
      - name: run integration tests
        run: |
              cd $APP_PATH
              ./test ${{ env.DEFAULT_RETAILER }} ${{ env.DEFAULT_ENV}} decanting 50
      # EXAMPLE: run tests for Albertsons env
      - name: run integration tests on abs ${{ env.DEFAULT_ENV}} where GOLD is enabled
        run: |
          cd $APP_PATH
          ./test abs ${{ env.DEFAULT_ENV}} decanting 50
      - name: Github checkout
          uses: actions/checkout@v3            
      - run: ${GITHUB_WORKSPACE}/.github/version.sh
          id: version
      # EXAMPLE: Notify via Slack message
      - name: Slack Notification
          if: ${{ failure() }}
          uses: rtCamp/action-slack-notify@v3
          env:
            SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
            SLACK_COLOR: ${{ job.status }}
            SLACK_USERNAME: Decanting service Bot
            SLACK_CHANNEL: team-fusion-alerts
            SLACK_TITLE: Integration tests status
            SLACK_MESSAGE: '[Karate] Tests execution on build: ${{ steps.version.outputs.version }} was ${{ job.status }}'
      # collect & push metrics to JIRA
      - name: Setup Golang
        if: always()
        uses: actions/setup-go@v3
        env:
            GITHUB_HEAD_REF: ${{ github.head_ref }}
          with:
            go-version: 1.17
      - run: |
          cd $APP_PATH/tests-automation-infrastructure/test-report-go-parser
          go run main.go
    
```