#!/usr/bin/env bash

# Only run if SUPPRESS_OPSGENIE env var is NOT set
if [[ -z $SUPPRESS_OPSGENIE ]]; then
  deployerEmail=$(yq '.clients.'$CLIENT'.deployerEmail' < ClientDeployers.yaml)

  curl -o /dev/null -s -w " -> %{http_code}\n" -X POST https://api.opsgenie.com/v2/alerts \
      -H "Content-Type: application/json" \
      -H "Authorization: GenieKey $OPSGENIE_KEY" \
      -d  '{
          "message": "[RTM]: '$typeOfFailure' Failure - '$CLIENT'-'$ENV'",
          "description": "Workflow Run:\n'$ghRunId'",
          "responders": [
              {"username": "'$deployerEmail'", "type": "user"},
              {"name": "RTM Deployments", "type": "team"}
          ],
          "visibleTo": [
              {"name":"domain-production", "type":"team"}
          ],
          "source": "RTM Repo",
          "tags": ["'$CLIENT'", "'$ENV'", "'$typeOfFailure'", "'$deployType'"]
      }'
fi
