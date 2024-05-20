#!/usr/bin/env bash

#Color Constants
NC='\033[0m' #No-Color
CYAN='\033[0;36m'

STATUSPAGE_PAGE="qth8l8vxd7y4"
FILE=INCIDENTS/${rt_version}_incidents.yaml

client=$clients #To make clear this is only 'one client'

#RTM and RN repos use different client identifiers (need a map)
declare -A clientMap=(
    ["abs"]="albertsons"
    ["blueberry"]="big-y"
    ["maf"]="maf"
    ["wings"]="woolworths"
    ["winter"]="wakefern"
    ["smu"]="smu"
    ["pinemelon"]="pinemelon"
    ["tienda"]="tienda-inglesa"
  )

get-operational-state() {
    result=$(curl -X GET https://api.statuspage.io/v1/pages/$STATUSPAGE_PAGE/incidents/$incidentId -H "Authorization: OAuth $STATUSPAGE_TOKEN")
    echo $result | jq '.status,.components[].status'
}


echo -e "\n${CYAN}Starting Statuspage processing...${NC}"
# echo "Get active maintenances"
result=$(curl -X GET https://api.statuspage.io/v1/pages/$STATUSPAGE_PAGE/incidents/active_maintenance -H "Authorization: OAuth $STATUSPAGE_TOKEN")

echo -e "\n${CYAN}Active Maintenances:${NC}"
echo $result | jq -r .[].id

#Get the maintenance incident ID for this client
client="${clientMap[$client]}" #Get set the client name as defined in the RN repo
incidentId=$(yq eval '.'$client $FILE)

echo -e "\n${CYAN}Looking for Active maintinance:${NC} Client=$client, IncidentId=$incidentId"

#Only act on active maintenance events
if [[ $result == *$incidentId* ]]; then

    echo -e "\n${CYAN}Active maintenance found:${NC} $incidentId"
    echo -e "\n${CYAN}Maintenance Initial State:${NC}"
    get-operational-state

    #Get components of the maintinence
    echo -e "\n${CYAN}Get maintenance components${NC}"
    result=$(curl -X GET https://api.statuspage.io/v1/pages/$STATUSPAGE_PAGE/incidents/$incidentId -H "Authorization: OAuth $STATUSPAGE_TOKEN")
    componentIds=$(echo $result | jq '.components[].id')

    ###
    # I thought this would set the components to operational, as 
    # 'auto_transition_to_operational_state' is set to true, but
    # it didn't (o maybe look into at a later date)
    #
    #Complete the maintenance-incident
    echo -e "\n${CYAN}Completing maintenance:${NC} $incidentId"
    curl https://api.statuspage.io/v1/pages/$STATUSPAGE_PAGE/incidents/$incidentId \
    -H "Authorization: OAuth $STATUSPAGE_TOKEN" \
    -X PATCH \
    -d "incident[status]=completed"

    # Now set the components
    echo -e "\n\n${CYAN}Set components to operational${NC}"
    for component in $componentIds;
    do
        component=$(echo $component | sed -e 's/^"//g;s/"$//g')  #Strip quotes off string

        curl https://api.statuspage.io/v1/pages/$STATUSPAGE_PAGE/components/$component\
        -H "Authorization: OAuth $STATUSPAGE_TOKEN" \
        -X PATCH \
        -d "component[status]=operational"
    done
else
    echo -e "\n${CYAN}### No ACTIVE Maintinenance Found For $client ###:${NC}"
    exit 1 #Failure (indicates need to send Slack msg)
fi

#Output Final State
echo -e "\n\n${CYAN}Maintenance End State:${NC}"
get-operational-state
exit 0
