#!/usr/bin/env bash

#****** Potential Updates
# -change from using env-vars to passing/reading vars
# -add help

#Color Constants
NC='\033[0m' #No-Color
RED='\033[0;31m'
GREEN='\033[0;32m'
U_CYAN='\033[4;36m'

SERVICES_GREP_STRING="auth-service|bifrost|cartonization|decanting-service|distiller|ims|integration-api|tom-api|service-catalog|osr-emulator"
RT_DIR=ReleaseTrains/$RT
if [[ ${RT} = RT* ]]; then
    RT_DIR=ReleaseTrains/20${RT: -2}/$RT
fi

failedServices=""
hasServiceOverrides=false

if test -f "$RT_DIR/$CLIENT/services.yaml"; then  #We need to check for overridden services
  hasServiceOverrides=true
  overriddenServices=$(yq '. | keys' < "$RT_DIR/$CLIENT/services.yaml"  | sed 's/^- //g')
fi

# We get all the pods in the ENV namespace (EXCLUDING mfc-code 9999) and output via `-o jsonpath` all containers images of those pods.
# Then we put each on its own line via `tr` and sort the output for unique values and grep out for takeoff labled services
#
# The resulting output is a list, one service per line, of: {serviceName}:{serviceVersion} (without the '{}'s)
# 
podData=$(kubectl get pods -n $ENV -l "takeoff.io/mfc-code"!="9999" -o jsonpath="{.items[*].spec.containers[*].image}" | tr -s '[:space:]' '\n' \
          | sort | uniq -c | grep takeoff | cut -d"/" -f 3)

printf "\nVerifying Deployed Services:\n\n"
printf "\t${U_CYAN}%-25s %-30s %s${NC}\n" "Service" "Deployed Version" "Expected Version" #Table Header
for x in $(echo "$podData" | grep -E $SERVICES_GREP_STRING); do
  read service version <<< "$(echo $x | sed 's/:/ /')"

  resultColor=${GREEN} #Start with failed (red) and change to success (green) once verified
  if [[ $ENV == "prod" && $service == "kisoft-osr-emulator" ]]; then
    :
  else
    printf "\t%-25s " $service
  fi

  case $service in
    "ims" | "distiller") #ims and distiller use image, not helm
      if [[ $hasServiceOverrides && $overriddenServices == *$service* ]]; then
        expectedVersion=$(yq eval '.'$service'.image' "$RT_DIR/$CLIENT/services.yaml")
      else
        expectedVersion=$(yq eval '.'$service'.image' "$RT_DIR/services.yaml")
      fi

      if [[ $version != $expectedVersion ]]; then
        failedServices+="$service "
        resultColor=${RED}
      fi
      printf "${resultColor}%-30s %s\n${NC}" "$version" "$expectedVersion"
      ;;

    "integration-api") #integration shows up as integration-api
      if [[ $hasServiceOverrides && $overriddenServices == *"integration"* ]]; then
       expectedVersion=$(yq eval '.integration.helm_chart_version' "$RT_DIR/$CLIENT/services.yaml")
      else
        expectedVersion=$(yq eval '.integration.helm_chart_version' "$RT_DIR/services.yaml")
      fi

      if [[ $version != $expectedVersion ]]; then
        failedServices+="integration "
        resultColor=${RED}
      fi
      printf "${resultColor}%-30s %s\n${NC}" "$version" "$expectedVersion"
      ;;

    "tom-api") #platform version is verified via tom-api
      if [[ $hasServiceOverrides && $overriddenServices == *"platform"* ]]; then
       expectedVersion=$(yq eval '.platform.helm_chart_version' "$RT_DIR/$CLIENT/services.yaml")
      else
        expectedVersion=$(yq eval '.platform.helm_chart_version' "$RT_DIR/services.yaml")
      fi
      
      if [[ $version != $expectedVersion ]]; then
        failedServices+="platform "
        resultColor=${RED}
      fi
      printf "${resultColor}%-30s %s\n${NC}" "$version" "$expectedVersion"
      ;;

    "kisoft-osr-emulator") #osr-emulator version is verified via kisoft-osr-emulator
      if [[ $ENV != "prod" ]]; then
        if [[ $hasServiceOverrides && $overriddenServices == *"osr-emulator"* ]]; then
        expectedVersion=$(yq eval '.osr-emulator.helm_chart_version' "$RT_DIR/$CLIENT/services.yaml")
        else
          expectedVersion=$(yq eval '.osr-emulator.helm_chart_version' "$RT_DIR/services.yaml")
        fi

        if [[ $version != $expectedVersion ]]; then
          failedServices+="osr-emulator "
          resultColor=${RED}
        fi
        printf "${resultColor}%-30s %s\n${NC}" "$version" "$expectedVersion"
      fi
      ;;

    *)
      if [[ $hasServiceOverrides && $overriddenServices == *$service* ]]; then
        expectedVersion=$(yq eval '.'$service'.helm_chart_version' "$RT_DIR/$CLIENT/services.yaml")
      else
        expectedVersion=$(yq eval '.'$service'.helm_chart_version' "$RT_DIR/services.yaml")
      fi

      if [[ $version != $expectedVersion ]]; then
        failedServices+="$service "
        resultColor=${RED}
      fi
      printf "${resultColor}%-30s %s\n${NC}" "$version" "$expectedVersion"
      ;;
  esac
done
echo ""

#Generate Return Results
if [[ $failedServices != "" ]]; then
  echo -e "There are failures:"
  echo -e "\t$failedServices"
  export FAILED_RTM_DEPLOYMENT_SERVICES=$failedServices
  export typeOfFailure=$(basename $0 .sh)
  ./scripts/triggerOpsgenieAlert.sh
  exit 1
else
  exit 0
fi

