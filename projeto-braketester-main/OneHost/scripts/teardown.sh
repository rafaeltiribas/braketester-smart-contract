##########################################################################
# INTER-NMI BLOCKCHAIN NETWORK EXPERIMENT - TEARDOWN - July/2020
# This script kills all the active docker containers and removes temp
# docker images, releasing disk space and letting the environment ready
# for a fresh restart. 
# Author: Wilson S. Melo Jr. - Inmetro
##########################################################################
#!/bin/bash

# Exit on first error, print all commands.
set -e

#tests if the user informed $1 parameter 
if [ -z "$1" ]
    then
        echo "Usage "$0" <docker-compose file>"
        exit 2
fi

#ask for confirmation
echo "THIS COMMAND WILL KILL AND REMOVE ALL YOUR ACTIVE DOCKER CONTAINERS!!!"
read -p "ARE YOU SURE? (Yy): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
    then        
        [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

# shutdown the docker containers informed in $1 parameter
# also remove orphans containers, which will include the orderer if it is in the local network
docker-compose -f $1 kill && docker-compose -f $1 down --remove-orphans  

# remove other "zumbi" containers
OTHL=$(docker ps -aq)
if [ ! -z "$OTHL" ]
    then
        echo "Removing lost containers..."
        docker rm -f $OTHL
fi

VOLUME=$(docker volume ls)
if [ ! -z "$VOLUME" ]
    then
        echo "Removing lost volumes..."
        docker volume rm -f $VOLUME
fi

# remove chaincode docker images (names start with "dev")
DEVL=$(docker images dev-* -q)
if [ ! -z "$DEVL" ]
    then
        echo "Removing chaincode containers dev-* images..."
        docker rmi -f $DEVL
fi

# Your system is now clean
