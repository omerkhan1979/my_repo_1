#!/bin/bash

set -ex

printenv

# check Pipeline Status (from Azure pipeline variables)
if [ "$PIPELINESTATUS" = "OK" ]; then
  STATUS="Success \ud83d\udc9a"
  ARGO_DEPLOY="is coming!"
else
  STATUS="Failed \ud83d\udca9"
  ARGO_DEPLOY="may not come :("
fi

# prepare text message for Slack
title='[shared tokens]'
author=$BUILD_SOURCEVERSIONAUTHOR

slack_text="Argo deploy ${ARGO_DEPLOY} \n
version will be deployed: \`${TAG_ID}\` \n
Build status: ${STATUS} \n
Author: \`${author}\`
"

# template Slack Json Payload
TEMPLATE='{"text": "","attachments": [{"title": "%s","color": "#4A98D6","text": "%s"}]}'
JSON=$(printf "$TEMPLATE" "$title" "$slack_text")

# debug output and write payload to the json file
echo "Slack payload.json: $JSON"
echo $JSON > payload.json

# send payload to Slack Webhook URL (from Azure pipeline Secrets)
curl -X POST -H 'Content-type: application/json' --data @payload.json ${SLACK_WEBHOOK}
rm payload.json
