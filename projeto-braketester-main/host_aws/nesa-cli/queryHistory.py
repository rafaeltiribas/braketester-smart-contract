"""
    The BlockMeter Experiment
    ~~~~~~~~~
    This module is necessary to register a meter in the blockchain. It
    receives the meter ID and its respective public key.
    This module must be called before any query against the ledger.
        
    :copyright: © 2020 by Wilson Melo Jr.
"""

import sys
from hfc.fabric import Client as client_fabric
import asyncio
import base64
import hashlib
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
#from ecdsa import SigningKey, NIST256p
#from ecdsa.util import sigencode_der, sigdecode_der

#For convencion, the first domain should be your admin domain.
domain = ["inmetro.br", "ptb.de"]
channel_name = "nmi-channel"
cc_name = "nmi"
cc_version = "1.0"
callpeer = []

#asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

if __name__ == "__main__":

    #test if the meter ID was informed as argument
    if len(sys.argv) != 2:
        print("Usage:",sys.argv[0],"<key>")
        exit(1)

    #get the meter ID
    key = sys.argv[1]
    
    #creates a loop object to manage async transactions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=("inmetro.br_aws.json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain[0], 'Admin')
    
    for i in domain:
    	callpeer.append("peer0." + i)
    print(callpeer)
    #callpeer = "peer0." + domain
    #callpeer = "peer0." + domain
    
    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually
    c_hlf.new_channel(channel_name)

    #invoke the chaincode to register the meter
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin, 
        channel_name=channel_name, 
        peers=callpeer,
        cc_name=cc_name, 
        fcn='countHistory', 
        args=[key], 
        cc_pattern=None))

    #the signature checking returned... (true or false)
    print("QueryHistory:\n", response)
    
