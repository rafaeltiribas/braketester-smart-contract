import asyncio
#from hfc.fabric_ca.caservice import ca_service
from hfc.fabric import Client as client_fabric
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import json
cc_version = "1.0"

class Sender():

    def __init__(self):
        self._data = None

    def send_to_api(self, data):

        if data is not None:
            asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

            c_hlf = client_fabric(net_profile="inmetro.br.json")


            admin = c_hlf.get_user('inmetro.br', 'Admin')


            # Make the client know there is a channel in the network
            c_hlf.new_channel('nmi-channel')

            loop = asyncio.get_event_loop()

            id ='888'

            #The response should be true if succeed
            response = loop.run_until_complete(c_hlf.chaincode_invoke(
                requestor=admin,
                channel_name='nmi-channel',
                peers=['peer0.inmetro.br', "peer0.ptb.de"],
                args=[id, data],
                cc_name='fabpki',
                fcn='insertMeasurement'
            ))
            print(response)
        else:
            return 'Dado vazio'

