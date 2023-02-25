#!/bin/bash

source scripts/utils.sh

# import utils
. scripts/envVar.sh

CHANNEL_NAME=${1:-"nmi-channel"}
CC_NAME=${2}
Args=${3}

export PATH=${PWD}/../fabric-samples/bin:$PATH
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="InmetroMSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/crypto-config/peerOrganizations/inmetro.br/peers/peer0.inmetro.br/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/crypto-config/peerOrganizations/inmetro.br/users/Admin@inmetro.br/msp
export CORE_PEER_ADDRESS=localhost:7051

println "executing with the following"
println "- CORE_PEER_TLS_ENABLED: ${C_GREEN}${CORE_PEER_TLS_ENABLED}${C_RESET}"
println "- CORE_PEER_LOCALMSPID: ${C_GREEN}${CORE_PEER_LOCALMSPID}${C_RESET}"
println "- CORE_PEER_TLS_ROOTCERT_FILE: ${C_GREEN}${CORE_PEER_TLS_ROOTCERT_FILE}${C_RESET}"
println "- CORE_PEER_MSPCONFIGPATH: ${C_GREEN}${CORE_PEER_MSPCONFIGPATH}${C_RESET}"
println "- CORE_PEER_ADDRESS: ${C_GREEN}${CORE_PEER_ADDRESS}${C_RESET}"


testChaincode() {
  parsePeerConnectionParameters $@
  res=$?
  verifyResult $res "Invoke transaction failed on channel '$CHANNEL_NAME' due to uneven number of peer and org parameters "
  
  set -x
  
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.nmi --tls --cafile $ORDERER_CA -C $CHANNEL_NAME -n ${CC_NAME} $PEER_CONN_PARMS -c ${Args}

  res=$?
  { set +x; } 2>/dev/null
  verifyResult $res "Invoke execution on $PEERS failed "
  successln "Invoke transaction successful on $PEERS on channel '$CHANNEL_NAME'"
}

total=0
#for i in $(seq 1 2); do
time="$(time (testChaincode) 2>&1 1>/dev/null)"
#total=`echo "$total + $time" | bc`
total=`echo "total=total;total+=time;total" | bc`

echo $time
echo $total
#avg=$(echo "$total" | bc)
#println "Avg Time: %.4f\n" $avg





exit 0
