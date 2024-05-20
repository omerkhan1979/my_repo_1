#!/usr/bin/env bash

blockDeployToFile=$1
allClients=$(paste -d, -s ALL_CLIENTS.yaml)
odeClients=$(paste -d, -s ODE_CLIENTS.yaml)
blockedClients=$(cat $blockDeployToFile | yq )

for clientEnv in $blockedClients;
do
    client=$(echo $clientEnv | cut -d"-" -f 1)
    env=$(echo $clientEnv | cut -d"-" -f 2)

    if [[ $allClients == *$client* || $odeClients == *$client* ]]; then
        case $env in
            qai|uat|prod)
                echo "Valid Env: $client-$env" ;;
            *)
                echo "Invalid Env: $client-$env"
                exit 1
                ;;
        esac
    else
        echo "ERROR: $client is not a valid client (see ALL_CLIENTS.yaml or ODE_CLIENTS.yaml)"
        exit 1
    fi
done

exit 0 #If we make it here... we're good
