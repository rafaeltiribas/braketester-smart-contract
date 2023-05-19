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
import json
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

domain = "inmetro.br" #you can change for "inmetro.br"
channel_name = "nmi-channel"
cc_name = "braketester"
cc_version = "1.0"


if __name__ == "__main__":
    # Substituir meter_id por placa do veículo. (Passar a placa no console).
    #test if the meter ID was informed as argument
    if len(sys.argv) != 2:
        print("Usage:",sys.argv[0],"<vehicle plate>")
        exit(1)

    #get the meter ID
    vehicle_plate = sys.argv[1]

    #format the name of the expected public key
    #pub_key_file = meter_id + ".pub"

    #try to retrieve the public key
    """ try:
        with open(pub_key_file, 'r') as file:
            pub_key = file.read()
    except:
        print("I could not find a valid public key to the meter",meter_id)
        exit(1) """

        
    #LER ARQUIVO .JSON CONTENDO OS DADOS DO FRENOMETRO
    with open('report-data.json', 'r') as file:
        reportData = json.load(file)
    print(reportData)
    #reportData = reportData['data']
    
    

    #   Transformar lista com os dados no tipo String para uma lista com os dados no tipo Byte.
    #encodedReportData = []
    #for x in reportData:
     #   x_encoded = x.encode('UTF-8')
      #  encodedReportData.append(x_encoded)

    #   Linhas para teste.
    '''
    print(reportData)
    print(encodedReportData)
    print(type(encodedReportData[0]))
    decodedData = []
    for x in encodedReportData:
        x_decoded = x.decode()
        decodedData.append(x_decoded)
    print(decodedData)
    '''

    #shows the meter public key
    #print("Continuing with the public key:\n",pub_key)

    #creates a loop object to manage async transactions
    loop = asyncio.get_event_loop()

    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain + ".json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain, 'Admin')
    callpeer = "peer0." + domain

    """ #query peer installed chaincodes, make sure the chaincode is installed
    print("Checking if the chaincode fabpki is properly installed:")
    response = loop.run_until_complete(c_hlf.query_installed_chaincodes(
        requestor=admin,
        peers=[callpeer]
    ))
    print(response) """

    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
    c_hlf.new_channel(channel_name)
    loop = asyncio.get_event_loop()
    asyncio.new_event_loop()
    #asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    
    print(type(vehicle_plate))
    #print(type(encodedReportData))
    #print(str(encodedReportData))
    print(str(reportData))

    #invoke the chaincode to register the meter
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin, 
        channel_name=channel_name, 
        peers=['peer0.inmetro.br'],
        args=[vehicle_plate, str(reportData)], 
        cc_name=cc_name,
        fcn='registerMeter', 
        ))

    #so far, so good
    print("Success on sending data report!")

