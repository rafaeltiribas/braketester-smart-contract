import json
import pickle
from hfc.fabric import Client as client_fabric
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
#from io import StringIO
#from datetime import datetime
#import sys
#import uuid

file_path = "2022-05-05_15_07_11_signal.pkl"
#bucket_name = record['s3']['bucket']['name']
#object_key = record['s3']['object']['key']

# get the numpy array object uploaded in S3

signal = pickle.load(open(file_path, "rb"))
#signal = pickle.loads(s3.Bucket(bucket_name).Object(object_key).get()['Body'].read())
# get data from onbject_key

signal_datetime = ('%Y-%m-%d_%H_%M_%S')
time_interval =  float(signal[0])

signal_data = signal[1:].tolist()
#signal_teste = bytes(json.dumps(signal_data, indent=2).encode('UTF-8'))

total_samples = len(signal_data)

# calculate sample rate
sr = int((1/time_interval))
total_in_sec = total_samples/sr

# good practices to receive the sensor id
sensor_id = 'Sensor_1_v2'
file_name = "teste.json"


Item = {
    'signal_data' : signal_data,  
    'sensor_id': sensor_id,
    
    'timestamp_signal': signal_datetime,
    'sampling_period_in_sec': format(time_interval, 'f'),
    'overall_samples': str(total_samples),
    'sample_rate_hz': str(sr),
    'total_of_seconds': str(total_in_sec),
    'signal_file_in_S3': file_name
    }
teste = json.dumps(Item, indent = 2).encode('UTF-8')
#teste2 = json.loads(teste)

#For convencion, the first domain should be your admin domain.
domain = ["inmetro.br", "nesa.br"]
channel_name = "nmi-channel"
cc_name = "nesa"
cc_version = "1.0"
callpeer = []
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
args=["666", teste],
cc_name=cc_name,
fcn='insertMeasurement'
))




