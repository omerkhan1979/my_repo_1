#!/usr/bin/env bash

host_regex="^host=\".*\""

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
cd ..

if [ -z "$1" ]
then
      	sed -i "s/$host_regex/host=\"calyx-api.tom.takeoff.com\"/g" githooks/pre-push
	
else
      	case $1 in
		dev)
			sed -i "s/$host_regex/host=\"calyx-api-dev.tom.takeoff.com\"/g" githooks/pre-push
			;;
		staging)
			sed -i "s/$host_regex/host=\"calyx-api-staging.tom.takeoff.com\"/g" githooks/pre-push
			;;
		prod)
			sed -i "s/$host_regex/host=\"calyx-api.tom.takeoff.com\"/g" githooks/pre-push
			;;
		*)
			sed -i "s/$host_regex/host=\"$1\"/g" githooks/pre-push
			;;
	esac
fi

find .git/hooks -type l -exec rm {} \;
find githooks -type f -exec ln -sf ../../{} .git/hooks/ \;