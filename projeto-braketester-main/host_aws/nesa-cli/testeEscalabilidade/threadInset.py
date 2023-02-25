from multiprocessing import Process
import sys
from hfc.fabric import Client as client_fabric
import asyncio
import json
import statistics
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import numpy as np
import math
import pandas as pd
from sympy import *
from scipy.stats import mode
import statistics 

#For convencion, the first domain should be your admin domain.
domain = ["inmetro.br", "nesa.br"]
channel_name = "nmi-channel"
cc_name = "fabpki"
cc_version = "1.0"
callpeer = []

#asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

def insertBlockchain1(meterid, filename):
    timestamp = []
    equip1 = []
    equip2 = []
    equip3 = []
    equip4 = []
    equip1_ = []
    equip2_ = []
    equip3_ = []
    equip4_ = []
    # iterate over the txt files in the folder
    with open(filename, "r", encoding="utf-8") as ficheiro:
        f = ficheiro.readlines()
        splitcontent = f[99000:-1]

        for v in splitcontent:
            v = v.split(sep=',', maxsplit=9)
            timestamp.append(v[0])
            equip1.append(float((v[1])))
            equip2.append(float((v[2])))
            equip3.append(float((v[3])))
            equip4.append(float((v[4])))

    equips = [equip1, equip2, equip3, equip4]
    equips_ = [equip1_, equip2_, equip3_, equip4_]
    for x in range(4):
        equips_[x].append(np.mean(equips[x]))
        equips_[x].append(np.median(equips[x]))
        #equips_[x].append(mode(equips[x]))
        #equips_[x].append(rms(equips[x]))
        equips_[x].append(desv_amostral(equips[x]))
        equips_[x].append(statistics.mode(equips[x]))
        equips_[x].append(np.var(equips[x]))
        #equips_[x].append(np.quantile(equips[x], .25))
        equips_[x].append((pd.DataFrame(equips[x])).mad())

        equips_[x].append(np.mean(np.diff(equips[x], n=1)))
        equips_[x].append(np.median(np.diff(equips[x], n=1)))
    #equips_[x].append(mode(np.diff(equips[x], n=1)))
        #equips_[x].append(rms(np.diff(equips[x], n=1)))
        equips_[x].append(desv_amostral(np.diff(equips[x], n=1)))
        equips_[x].append(statistics.mode(np.diff(equips[x], n=1)))
        equips_[x].append(np.var(np.diff(equips[x], n=1)))
    #equips_[x].append(np.quantile((np.diff(equips[x], n=1)), .25))
        equips_[x].append((pd.DataFrame(np.diff(equips[x], n=1)).mad()))

        equips_[x].append(media(np.diff(equips[x], n=2)))
        equips_[x].append(np.median(np.diff(equips[x], n=2)))
        #equips_[x].append(mode(np.diff(equips[x], n=2)))
        #equips_[x].append(rms(np.diff(equips[x], n=2)))
        equips_[x].append(desv_amostral(np.diff(equips[x], n=2)))
        equips_[x].append(statistics.mode(np.diff(equips[x], n=2)))
        equips_[x].append(np.var(np.diff(equips[x], n=2)))
        #equips_[x].append(np.quantile((np.diff(equips[x], n=1)), .25))
        equips_[x].append((pd.DataFrame(np.diff(equips[x], n=2)).mad()))

    jsonStructure = {
        "Media": equips_[0][0],
        "Mediana": equips_[0][1],
        "DesvAmostral": equips_[0][2],
        "Moda": equips_[0][3],
        "Variancia": equips_[0][4],
        "Mad": equips_[0][5][0],

        "Media2": equips_[1][0],
        "Mediana2": equips_[1][1],
        "DesvAmostral2": equips_[1][2],
        "Moda2": equips_[1][3],
        "Variancia2": equips_[1][4],
        "Mad2": equips_[1][5][0],

        "Media3": equips_[2][0],
        "Mediana3": equips_[2][1],
        "DesvAmostral3": equips_[2][2],
        "Moda3": equips_[2][3],
        "Variancia3": equips_[2][4],
        "Mad3": equips_[2][5][0],

        "Media4": equips_[3][0],
        "Mediana4": equips_[3][1],
        "DesvAmostral4": equips_[3][2],
        "Moda4": equips_[3][3],
        "Variancia4": equips_[3][4],
        "Mad4": equips_[3][5][0],
    }
    data = json.dumps(jsonStructure, indent=4)

    #print(data)
    #creates a loop object to manage async transactions
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
    peers=['peer0.inmetro.br', "peer0.nesa.br"],
    args=[meterid, data],
    cc_name='nesa',
    fcn='insertMeasurement'
    ))

    #so far, so good
    print("1- Success on inserting the measurement in the blockchain")

def insertBlockchain2(meterid, filename):

    timestamp = []
    equip1 = []
    equip2 = []
    equip3 = []
    equip4 = []
    equip1_ = []
    equip2_ = []
    equip3_ = []
    equip4_ = []
    # iterate over the txt files in the folder
    with open(filename, "r", encoding="utf-8") as ficheiro:
        f = ficheiro.readlines()
        splitcontent = f[99000:-1]

        for v in splitcontent:
            v = v.split(sep=',', maxsplit=9)
            timestamp.append(v[0])
            equip1.append(float((v[1])))
            equip2.append(float((v[2])))
            equip3.append(float((v[3])))
            equip4.append(float((v[4])))

    equips = [equip1, equip2, equip3, equip4]
    equips_ = [equip1_, equip2_, equip3_, equip4_]
    for x in range(4):
        equips_[x].append(np.mean(equips[x]))
        equips_[x].append(np.median(equips[x]))
        #equips_[x].append(mode(equips[x]))
        #equips_[x].append(rms(equips[x]))
        equips_[x].append(desv_amostral(equips[x]))
        equips_[x].append(statistics.mode(equips[x]))
        equips_[x].append(np.var(equips[x]))
        #equips_[x].append(np.quantile(equips[x], .25))
        equips_[x].append((pd.DataFrame(equips[x])).mad())

        equips_[x].append(np.mean(np.diff(equips[x], n=1)))
        equips_[x].append(np.median(np.diff(equips[x], n=1)))
    #equips_[x].append(mode(np.diff(equips[x], n=1)))
        #equips_[x].append(rms(np.diff(equips[x], n=1)))
        equips_[x].append(desv_amostral(np.diff(equips[x], n=1)))
        equips_[x].append(statistics.mode(np.diff(equips[x], n=1)))
        equips_[x].append(np.var(np.diff(equips[x], n=1)))
    #equips_[x].append(np.quantile((np.diff(equips[x], n=1)), .25))
        equips_[x].append((pd.DataFrame(np.diff(equips[x], n=1)).mad()))

        equips_[x].append(media(np.diff(equips[x], n=2)))
        equips_[x].append(np.median(np.diff(equips[x], n=2)))
        #equips_[x].append(mode(np.diff(equips[x], n=2)))
        #equips_[x].append(rms(np.diff(equips[x], n=2)))
        equips_[x].append(desv_amostral(np.diff(equips[x], n=2)))
        equips_[x].append(statistics.mode(np.diff(equips[x], n=2)))
        equips_[x].append(np.var(np.diff(equips[x], n=2)))
        #equips_[x].append(np.quantile((np.diff(equips[x], n=1)), .25))
        equips_[x].append((pd.DataFrame(np.diff(equips[x], n=2)).mad()))

    jsonStructure = {
        "Media": equips_[0][0],
        "Mediana": equips_[0][1],
        "DesvAmostral": equips_[0][2],
        "Moda": equips_[0][3],
        "Variancia": equips_[0][4],
        "Mad": equips_[0][5][0],

        "Media2": equips_[1][0],
        "Mediana2": equips_[1][1],
        "DesvAmostral2": equips_[1][2],
        "Moda2": equips_[1][3],
        "Variancia2": equips_[1][4],
        "Mad2": equips_[1][5][0],

        "Media3": equips_[2][0],
        "Mediana3": equips_[2][1],
        "DesvAmostral3": equips_[2][2],
        "Moda3": equips_[2][3],
        "Variancia3": equips_[2][4],
        "Mad3": equips_[2][5][0],

        "Media4": equips_[3][0],
        "Mediana4": equips_[3][1],
        "DesvAmostral4": equips_[3][2],
        "Moda4": equips_[3][3],
        "Variancia4": equips_[3][4],
        "Mad4": equips_[3][5][0],
    }
    data = json.dumps(jsonStructure, indent=4)

    #print(data)
    #creates a loop object to manage async transactions
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
    peers=['peer0.inmetro.br', "peer0.nesa.br"],
    args=[meterid, data],
    cc_name='nesa',
    fcn='insertMeasurement'
    ))

    #so far, so good
    print("2 - Success on inserting the measurement in the blockchain")


def media(equip):
  return np.mean(equip)

def rms(equip):
  rms = 0
  for i in range(len(equip1)):
    rms = rms + equip1[i]**2
  rms = math.sqrt(rms/len(equip1))
  return rms
  #print('rms:', rms)

def desv_amostral(equip):
  return statistics.stdev(equip)
  #desv_amostral = statistics.stdev(equip1)
  #print ('Desvio padrão da amostra:',desv_amostral)
          
def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

while(True):
    runInParallel(insertBlockchain1("666","setup8_cenario1_03.txt"), insertBlockchain2("666","setup8_cenario1_02.txt"))
