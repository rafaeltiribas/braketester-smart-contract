# Imports
import csv, sys
import sys, os
import time as t
from datetime import datetime
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join
import json
import random
from time import time




dir_base = './setup8'

# list all files from directory
files = [f for f in listdir(dir_base) if isfile(join(dir_base, f)) and f.endswith('.txt')]
print(files)

# Reading data file




def readfile(filename):

    df = pd.DataFrame()
    target = []
    sr = []
    freq = []
    file = filename
    print(file)
    times = []
    sensor1 = []
    sensor2 = []
    sensor3 = []
    sensor4 = []
    
    #Reading file
    with open(file) as f:
        cont = 0

        #get all the lines from text file
        lines = f.readlines()
        total_lines = len(lines)
        
        if total_lines > 100023:
            total_lines = 100023
        if total_lines > 50023 and total_lines < 50030:
            total_lines = 50023

        print('Reading file {} with {} lines'.format(file, total_lines))

        freq.append(file.split('_')[1].replace('.txt', ''))
        
        # Try to read one line at a time
        try:
            for line in lines:
                cont = cont+1
                strip = line.rstrip("\n")
                strip = strip.split(',')
                
                if cont == 20:
                    sr.append(float(strip[1]))

                # Here, we use this 'if' to exclude the header
                if cont > 22 and cont < total_lines:
                    try:
                        # Adding the values to their respective variables
                        times.append(float(strip[0]))
                        sensor1.append(float(strip[1]))
                        sensor2.append(float(strip[2]))
                        sensor3.append(float(strip[3]))
                        sensor4.append(float(strip[4]))
                        
                    except:
                        print('ERRO na linha {} do arquivo {}'.format(cont, file))
                        print(strip)
                        print(strip[0])
                        sys.exit('ERRO - Verificar arquivo de dados')

        except csv.Error as e:
            sys.exit('arquivo %s, linha %d: %s' % (file, f.line_num, e))


    partition = 50000
    for x in range (0, total_lines-23, partition):
        df = pd.concat([df, pd.DataFrame(sensor1[x:x+partition]).transpose()], ignore_index=True)
        target.append('Sensor I01')
        df = pd.concat([df, pd.DataFrame(sensor2[x:x+partition]).transpose()], ignore_index=True)
        target.append('Sensor I02')
        df = pd.concat([df, pd.DataFrame(sensor3[x:x+partition]).transpose()], ignore_index=True)
        target.append('Sensor I03')
        df = pd.concat([df, pd.DataFrame(sensor4[x:x+partition]).transpose()], ignore_index=True)
        target.append('Sensor I04')

    setup1 = df.T

    equip1 = str(((setup1.loc[0:49999,0:0]).values).tolist())

    jsonStructure = {
		"Equip1": equip1,
    }

    data = json.dumps(jsonStructure, indent=4)
    
    return data
	
data2 = readfile('setup8/setup8_cenario1_02.txt')
print(len(data2))


