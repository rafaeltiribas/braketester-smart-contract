"""
    The BlockMeter Experiment
    ~~~~~~~~~
    This module is necessary to register a meter in the blockchain. It
    receives the meter ID and its respective public key.
    This module must be called before any query against the ledger.
        
    :copyright: 2020 by Wilson Melo Jr.
"""

import sys
from hfc.fabric import Client as client_fabric
import asyncio

domain = "ptb.de" #you can change for "inmetro.br"
channel_name = "nmi-channel"
cc_name = "fabpki"
cc_version = "1.0"

if __name__ == "__main__":

    #test if the meter ID was informed as argument
    if len(sys.argv) != 2:
        print("Usage:",sys.argv[0],"<meter id>")
        exit(1)

    #get the meter ID
    meter_id = sys.argv[1]

    #format the name of the expected public key
    pub_key_file = meter_id + ".pub"



    #LER ARQUIVO DO RELATORIO E ARMAZENAR LISTA NA VARIAVEL REPORTDATA
    file = open('report-data.csv', 'r')
    fileLine = file.readlines()
    count = 0
    reportData = []
    for line in fileLine:
    	count += 1
    	reportData.append(line)
    print("File read.")
    	
    	

    #shows the meter public key
    print("Continuing with the public key:\n",pub_key)

    #creates a loop object to manage async transactions
    loop = asyncio.get_event_loop()

    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain + ".json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain, 'Admin')
    callpeer = "peer0." + domain

    #query peer installed chaincodes, make sure the chaincode is installed
    print("Checking if the chaincode fabpki is properly installed:")
    response = loop.run_until_complete(c_hlf.query_installed_chaincodes(
        requestor=admin,
        peers=[callpeer]
    ))
    print(response)

    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
    c_hlf.new_channel(channel_name)

    #invoke the chaincode to register the meter
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin, 
        channel_name=channel_name, 
        peers=[callpeer],
        cc_name=cc_name, 
        cc_version=cc_version,
        fcn='registerMeter', 
        args=[meter_id, pub_key, reportData], 
        cc_pattern=None))

    #so far, so good
    print("Success on sending data report!")

