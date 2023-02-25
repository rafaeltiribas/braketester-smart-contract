import json
from hfc.fabric import Client as client_fabric
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

#For convencion, the first domain should be your admin domain.
domain = ["inmetro.br", "nesa.br"]
channel_name = "nmi-channel"
cc_name = "nesa"
cc_version = "1.0"
callpeer = []

f = open('2022-06-24_13_18_33_signal_2Sensors.json')
signal = json.load(f)
signal = json.dumps(signal)


def insert(signal):

	data = json.loads(signal)

	for sensor in range(len(data['signals'])):

		id = data['hardware_id'] + data['signals'][sensor]['sensor_id']
		
		Sensor_data = { 
			'timestamp_signal': data['timestamp_signal'],  
			'sampling_period_in_sec': data['signals'][sensor]['sampling_period_in_sec'],
			'overall_samples:': data['signals'][sensor]['overall_samples:'],
			'sample_rate_hz': data['signals'][sensor]['sample_rate_hz'],
			'total_of_seconds': data['signals'][sensor]['total_of_seconds'],
			'signal_data' : data['signals'][sensor]['signal_data']
		}

		Sensor_data = json.dumps(Sensor_data, indent = 2).encode('UTF-8')
		

		loop = asyncio.get_event_loop()

		#instantiate the hyperledeger fabric client
		c_hlf = client_fabric(net_profile=("inmetro.br.json"))

		#get access to Fabric as Admin user
		admin = c_hlf.get_user(domain[0], 'Admin')

		for i in domain:
			callpeer.append("peer0." + i)

		#the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
		c_hlf.new_channel(channel_name)
		asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
		#invoke the chaincode to register the meter
		response = loop.run_until_complete(c_hlf.chaincode_invoke(
		requestor=admin,
		channel_name='nmi-channel',
		peers=['peer0.inmetro.br'],
		args=[id, Sensor_data],
		cc_name=cc_name,
		fcn='insertMeasurementAWS'
		))
		
		return "Sucess"
		
insert(signal)

