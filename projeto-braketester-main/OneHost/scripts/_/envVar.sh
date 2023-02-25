#!/bin/bash
#
# Copyright IBM Corp All Rights Reserved
#
# SPDX-License-Identifier: Apache-2.0
#

# This is a collection of bash functions used by different scripts

# imports
. scripts/utils.sh

export CORE_PEER_TLS_ENABLED=true
export ORDERER_CA=${PWD}/crypto-config/ordererOrganizations/orderer.nmi/orderers/orderer.nmi.orderer.nmi/msp/tlscacerts/tlsca.orderer.nmi-cert.pem
export PEER0_ORG1_CA=${PWD}/crypto-config/peerOrganizations/inmetro.br/peers/peer0.inmetro.br/tls/ca.crt
export PEER0_ORG2_CA=${PWD}/crypto-config/peerOrganizations/nesa.br/peers/peer0.nesa.br/tls/ca.crt
export PEER0_ORG3_CA=${PWD}/crypto-config/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt

# Set environment variables for the peer org
setGlobals() {
  local USING_ORG=""
  if [ -z "$OVERRIDE_ORG" ]; then
    USING_ORG=$1
  else
    USING_ORG="${OVERRIDE_ORG}"
  fi
  infoln "Using organization ${USING_ORG}"
  if [ $USING_ORG == "inmetro.br" ]; then
    export CORE_PEER_LOCALMSPID="InmetroMSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_ORG1_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/crypto-config/peerOrganizations/inmetro.br/users/Admin@inmetro.br/msp
    export CORE_PEER_ADDRESS=localhost:7051
  elif [ $USING_ORG == "nesa.br" ]; then
    export CORE_PEER_LOCALMSPID="NESAMSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_ORG2_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/crypto-config/peerOrganizations/nesa.br/users/Admin@nesa.br/msp
    export CORE_PEER_ADDRESS=localhost:9051

  elif [ $USING_ORG == "org3" ]; then
    export CORE_PEER_LOCALMSPID="Org3MSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_ORG3_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/crypto-config/peerOrganizations/org3.example.com/users/Admin@org3.example.com/msp
    export CORE_PEER_ADDRESS=localhost:11051
  else
    errorln "ORG Unknown"
  fi

  if [ "$VERBOSE" == "true" ]; then
    env | grep CORE
  fi
}



# Set environment variables for use in the CLI container 
setGlobalsCLI() {
  setGlobals $1

  local USING_ORG=""
  if [ -z "$OVERRIDE_ORG" ]; then
    USING_ORG=$1
  else
    USING_ORG="${OVERRIDE_ORG}"
  fi
  if [ $USING_ORG == "inmetro.br" ]; then
    export CORE_PEER_ADDRESS=peer0.inmetro.br:7051
  elif [ $USING_ORG == "nesa.br" ]; then
    export CORE_PEER_ADDRESS=peer0.nesa.br:9051
  else
    errorln "ORG Unknown"
  fi
}

# parsePeerConnectionParameters $@
# Helper function that sets the peer connection parameters for a chaincode
# operation
parsePeerConnectionParameters() {
  PEER_CONN_PARMS=""
  PEERS=""
  while [ "$#" -gt 0 ]; do
    #setGlobalsCLI $1
    if [ $1 -eq 1 ]; then
      setGlobals inmetro.br
      PEER="peer0.inmetro.br"
    elif [ $1 -eq 2 ]; then
      setGlobals nesa.br
      PEER="peer0.nesa.br"
    fi
    ## Set peer addresses
    PEERS="$PEERS $PEER"
    PEER_CONN_PARMS="$PEER_CONN_PARMS --peerAddresses $CORE_PEER_ADDRESS"
    ## Set path to TLS certificate
    TLSINFO=$(eval echo "--tlsRootCertFiles \$PEER0_ORG$1_CA")
    PEER_CONN_PARMS="$PEER_CONN_PARMS $TLSINFO"
    # shift by one to get to the next organization
    shift
  done
  # remove leading space for output
  PEERS="$(echo -e "$PEERS" | sed -e 's/^[[:space:]]*//')"
}

verifyResult() {
  if [ $1 -ne 0 ]; then
    fatalln "$2"
  fi
}
