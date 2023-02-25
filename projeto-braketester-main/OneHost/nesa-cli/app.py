# from flask import Flask, jsonify
import os
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields

#imports from blockchain
import sys
from hfc.fabric import Client as client_fabric
import asyncio
import base64
import hashlib
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sigencode_der, sigdecode_der

app = Flask(__name__)

# Descrição do app
app_infos = dict(version='1.0', title='nmiblockchain',
                 description='To access the chaincode using this application, select the post method, click "try out", fill in the json file and run.',
                 contact_email='caruviaro@outlook.com'#,prefix='/eee'
                )

# inicia o swagger app
rest_app = Api(app, **app_infos)


db_model = rest_app.model('Variáveis usadas no primeiro modelo',
	{
    'args': fields.List(cls_or_instance= fields.String, required = True,
					 description="argumentos da função",
					 help="Ex. meter_id, message, b64sig"),
   'domain': fields.List(cls_or_instance= fields.String, required = True,
           description = "Domínios",
                           help="Ex. [inmetro.br, ptb.de]"),
   'channel_name': fields.String(required=True,
                                  description="Nome do canal"),
   'cc_name': fields.String(required = True,
           description = "Nome do chaincode" ),
   'function': fields.String(required = True,
           description = "Função do chaincode a ser executada" )
     })

# @app.route("/consult")
# def consult():
#   #array_do_usuario = np.array([array_do_usuario])
#   #pred = modelo_carregado.predict(array_do_usuario.reshape(1,-1))
#   return (f"sua solicitação foi predita como: ok", 200)

## Vamos organizar os endpoints por aqui!
# link gerado será: http://127.0.0.1:5000/primeiro_endpoint_swagger

    
consult = rest_app.namespace('', description='Here we will execute the chaincode functions .')
@consult.route("/")
class Teste(Resource):
    @rest_app.expect(db_model)
    #@rest_app.marshal_with(db_model)
    def post(self):
        args = request.json['args']
        domain = request.json['domain']
        channel_name = request.json['channel_name']
        cc_name = request.json['cc_name']
        function = request.json['function']
        return {
                "status": "OK",
                "valor" : select_function(args, domain, channel_name, cc_name, function)
               } 
    def get(self):        
    	return {
    		"status": "OK",  
        }

def select_function(args, domain, channel_name, cc_name, function):
	if function == "registerMeter":
		return register_ecdsa(args, domain, channel_name, cc_name, function)
	elif function == "checkSignature":
		return verify_ecdsa(args, domain, channel_name, cc_name, function)
	else:
		return "Error on retrieving" 

def verify_ecdsa(args, domain, channel_name, cc_name, function):

    # get the meter ID
    meter_id = args[0]
    message = args[1]
    callpeer = []

    # format the name of the expected private key
    priv_key_file = meter_id + ".priv"

    # try to retrieve the private key
    try:
        print(priv_key_file)
        with open(priv_key_file, 'r') as file:
            priv_key = SigningKey.from_pem(file.read())
    except:
        print("I could not find a valid private key to the meter", meter_id)
        exit(1)

    # signs the message using the private key and converts it to base64 encoding
    signature = priv_key.sign(message.encode(), hashfunc=hashlib.sha256, sigencode=sigencode_der)
    b64sig = base64.b64encode(signature)

    # giving the signature feedback
    print("Continuing with the information...\nmessage:", message, "\nsignature:", b64sig)

    # creates a loop object to manage async transactions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain[0] + ".json"))

    # get access to Fabric as Admin user
    admin = c_hlf.get_user(domain[0], 'Admin')
    for i in domain:
    	callpeer.append("peer0." + i)

    # the Fabric Python SDK do not read the channel configuration, we need to add it mannually
    c_hlf.new_channel(channel_name)

    # invoke the chaincode to register the meter
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin,
        channel_name=channel_name,
        peers=callpeer,
        cc_name=cc_name,
        fcn=function,
        args=[meter_id, message, b64sig],
        cc_pattern=None))

    # the signature checking returned... (true or false)
    print("The signature verification returned:\n", response)
    return response
    
def register_ecdsa(args, domain, channel_name, cc_name, function):

    #get the meter ID
    meter_id = args[0]

    #format the name of the expected public key
    pub_key_file = meter_id + ".pub"
    callpeer = []
    #try to retrieve the public key
    try:
        with open(pub_key_file, 'r') as file:
            pub_key = file.read()
    except:
        print("I could not find a valid public key to the meter",meter_id)
        exit(1)

    #shows the meter public key
    print("Continuing with the public key:\n",pub_key)

    #creates a loop object to manage async transactions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain[0] + ".json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain[0], 'Admin')
    for i in domain:
    	callpeer.append("peer0." + i)

    #query peer installed chaincodes, make sure the chaincode is installed
    print("Checking if the chaincode fabpki is properly installed:")
    response = loop.run_until_complete(c_hlf.query_installed_chaincodes(
        requestor=admin,
        peers=[callpeer[0]]
    ))
    print(response)

    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
    c_hlf.new_channel(channel_name)

    #invoke the chaincode to register the meter
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin, 
        channel_name=channel_name, 
        peers=callpeer,
        cc_name=cc_name, 
        fcn=function, 
        args=[meter_id, pub_key], 
        cc_pattern=None))
 
    #so far, so good 
    print("Success on register meter and public key!")
    return "Success on register meter and public key!"

if __name__ == "__main__":
  debug = True # com essa opção como True, ao salvar, o "site" recarrega automaticamente.
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=debug)
