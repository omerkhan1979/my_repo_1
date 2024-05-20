#!/usr/bin/env bash

#Color Constants
NC='\033[0m' #No-Color
RED='\033[0;31m'

FAILED_DEPLOY_HEALTH_STR="FAILED Deployments Health"
GET_PODS_FILE="getPodsResults.log"
FAILED_DEPLOYMENTS_FILE="failedDeployments.log"
DEPLOYMENTS_STATUS_FILE="deploymentsStatus.yaml"

rm -f $FAILED_DEPLOYMENTS_FILE

kubectl get pods -n $ENV | grep -v backup-util > $GET_PODS_FILE
kubectl get deployments -n $ENV -o yaml > $DEPLOYMENTS_STATUS_FILE

# Gets the status section of the `get deployments` results and selects only those that have a mismatch between expected and action replicas.
# It then takes those returns and outputs the name of the service via the parent structure's metadata.name field
failedServices=$(yq '.items[].status | select(.readyReplicas != .replicas and .availableReplicas != .replicas) | parent | .metadata.name' < $DEPLOYMENTS_STATUS_FILE)

echo "Verifying Deployment Health..."
cat $GET_PODS_FILE #Output `get pods`` into GH Workflow log

for service in $failedServices;
do
  if [[ $service == "backup-util" ]]; then
    continue
  fi
  #Ouput into GH Workflow log
  reason=$(cat $GET_PODS_FILE | grep $service | awk '{print $3}')
   
  printf "\n${RED}$FAILED_DEPLOY_HEALTH_STR (%s):${NC} %s\n" $reason $service
  yq '.items[] | select(.metadata.name == "'$service'") | .status' < $DEPLOYMENTS_STATUS_FILE

  #Output to file for later use in Opsgenie alert
  echo -e "\n$FAILED_DEPLOY_HEALTH_STR ($reason): $service:" >> $FAILED_DEPLOYMENTS_FILE
  echo $(yq '.items[] | select(.metadata.name == "'$service'") | .status' < $DEPLOYMENTS_STATUS_FILE >> $FAILED_DEPLOYMENTS_FILE)

done

if [[ -f $FAILED_DEPLOYMENTS_FILE ]]; then
  export FAILED_DEPLOYMENTS_SERVICES=$failedServices
  export typeOfFailure=$(basename $0 .sh)
  ./scripts/triggerOpsgenieAlert.sh
  exit 1
else
  echo "Deployments Health: SUCCESS"
  exit 0
fi
