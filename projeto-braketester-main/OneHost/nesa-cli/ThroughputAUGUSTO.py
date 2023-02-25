import sys
import os
# import signal
import math
import random
import time
import array as arr
from hfc.fabric import Client as client_fabric
import asyncio
import json
import pickle
import threading
import multiprocessing as mp
import csv
import string
import numpy as np
import statistics
import pandas as pd

# defines the chaincode version
cc_version = "1.0"
encrypted_values = []
maxrand = 99
data = ""
domain = ["inmetro.br", "nesa.br"]
channel_name = "nmi-channel"
cc_name = "nesa"
cc_version = "1.0"
callpeer = []

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


def gerar_chave(size=12, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def media(equip):
    return np.mean(equip)


def rms(equip):
    rms = 0
    for i in range(len(equip1)):
        rms = rms + equip1[i] ** 2
    rms = math.sqrt(rms / len(equip1))
    return rms
    # print('rms:', rms)


def desv_amostral(equip):
    return statistics.stdev(equip)


class TransactionThread(threading.Thread):
    """We implement a class to encapsulate threads.
    The send_transaction() method does all the job.

    Atributes:
        meter_id (str): the identifier of the meter
        pub_key (str): the Paillier public key
        thread_id: the sequencial thread_id, which dependes on
            the number of threads you create.
        c_lock: a thread locker (a mutex) to deal with
            concurrency in some specific functions of the Fabric SDK
        c_event: a shared thread event object to notify the
            threads that they must stop.
    Methods:
        send_transaction(): treats the OPCUA communication and implements
        the respective chaincode invoke.
    """

    def __init__(self, thread_id, c_lock, c_event):
        threading.Thread.__init__(self)
        # computes an unique ID to the meter. The formula must be the same used in prepare-morph-mp.py
        self.meter_id = str((mp.current_process()._identity[0] - 1) * 10000 + thread_id * 100)

        # make a simple attribution of the other parameters
        # self.mode = mode
        # self.pub_key = pub_key
        # self.kbits = kbits
        self.c_lock = c_lock
        self._stopevent = c_event

    def run(self):
        """This method deals with control procedures related to the thread.
        It calls the send_transaction() method, and after it saves any statistics
        related to the transaction spent time.
        """
        # use print to log everything you need
        print("Starting...: " + self.meter_id)

        # send transaction to the endorser and to the order
        self.send_transactions()

        print("Exiting...: " + self.meter_id)

    def send_transactions(self):
        """This method implements the thralso ead execution code. It basically collects
        measurements from a UPCUA server also and adds these new measurements to the
        consumption value in the ledger. also If the meter_id has a pair of Paillier keys,
        it sends a encrypted measurement also by invoking insertMeasurement chaincode.
        Otherwise, it sends a plaintext malso easurement by invoking insertPlaintextMeasurement
        chaincode. On it transaction, it also collects start and end times, logging them in the
        statistics vector.

        Notice that the Fabric invoke chaincode performs a transcation in two steps.
        First, the transaction is sent to a endorser peer. This call blocks the client
        (i.e., the client waits by the endorser response until a default timeout).
        After, the client sends the endorsed transaction to the orderer service, but do not
        wait by a response anymore. All these steps are encapsulated by the Fabric SDK.
        """
        # creates a loop object to manage async transactions
        loop = asyncio.new_event_loop()
        # configures the event loop of the current thread
        asyncio.set_event_loop(loop)

        # The function that starts the Fabric SDK does not support concurrency,
        # so we need the locker to synchronize the multithread access.
        self.c_lock.acquire(1)

        # we also creates a control to try again just in case the access to the SDK fails
        stop = False
        while not stop:
            try:
                # instantiate the Fabric SDK client (ptb-network.json is our network profile)
                c_hlf = client_fabric(net_profile=("inmetro.br.json"))
                stop = True
            except:
                stop = False
            # now we can release the locker...
        self.c_lock.release()

        # get access to Fabric as Admin user
        admin = c_hlf.get_user('inmetro.br', 'Admin')
        # the Fabric Python SDK do not read the channel configuration, we need to add it mannually
        c_hlf.new_channel('nmi-channel')

        # we will change the meter_id within an offset to reduce the probability of key collision
        id_offset = 0
        max_offset = 100

        encrypted = ""

        # the thread runs until the main program requests its stop
        while not self._stopevent.isSet():
            try:
                # generates a random measurement value between 1 and 99
                measurement = random.randint(1, maxrand)

                # modify the meter_id value
                meter_id_temp = str(int(self.meter_id) + id_offset)

                # test if pub_key is valid
                
                
                
                
                # invoke the LR chaincode...
                print("insertPlainTextMeasurement:(t=" + meter_id_temp + ",m=" + str(measurement) + ")")

                # take time measurement to generate statistics
                start = time.time()

                # the transaction calls chaincode 'insertPlainTextMeasurement'. It uses the meter ID for
                # inserting the new measurement. Admin is used.
                loop.run_until_complete(c_hlf.chaincode_invoke(
                    requestor=admin,
                    channel_name='nmi-channel',
                    peers=['peer0.inmetro.br'],
                    args=[gerar_chave(), data],
                    cc_name='nesa',
                    fcn='insertMeasurement'
                ))
                

            # take time measurement to generate statistics
                end = time.time()

            # append statistics to the respective list
            #    self.statistics.append([start,end])

            # increments id_offset, reseting it when it is equal or greater than max_offset
                id_offset = (id_offset + 1) % max_offset

                # each thread generates 1 tsp... so it is time to sleep a little :-)
                sleep_time =1-( end - start)
                if sleep_time > 0:
                
                	time.sleep(sleep_time)	

                # so far, so good
                # print("Insertion OK, getting next measurement...")

            except:
            # exceptions probably occur when the transaction fails. In this case, we
            # need to adjust the id_offset, so the thread has high chances of continue
            # executing with the next meter ID.
                id_offset = (id_offset + 1) % max_offset

            # self.c_lock.release()
                print("We are having problems with the exceptions...")


def multiproc(mnt, slp, lock):
    # creates a locker to synchronize the threads
    c_lock = lock
    c_event = threading.Event()

    # creates a vector to keep the threads reference and join all them later
    threads = []

    # loop to create all the required threads
    for x in range(mnt):
        # creates the x-th thread
        t = TransactionThread(x, c_lock, c_event)
        # add the thread to the reference vector
        threads.append(t)
        # starts the thread
        t.start()

    # let the threads run for the next slp seconds...
    time.sleep(slp)

    # notify the threads that they need to stop
    c_event.set()

    # recall the join for all create threads
    for t in threads:
        t.join()


if __name__ == "__main__":
    data = readfile("setup8/setup8_cenario1_02.txt")
    #data = "[187152, 130204, 30290, 39158, 897103, 65566, 517088, 188175, 312017, 258377, 37004, 365225, 333871, 607226, 1117207, 366791, 558506, 294980, 167202, 110191]"

    # get the number of threads and benchmark mode
    nprocesses = int(sys.argv[1])
    nthreads = int(sys.argv[2])

    # treats the public key (if it was provided)

    # randomize our entropy source...
    random.seed(123)

    # if necessary, use this line to stop the multiprocessing execution until the user confirms
    # input('Ready to create the multiprocesses. Press ENTER to start...\n')

    # start subprocess to execute script which collects CPU statistics

    # setup a list of processes that we want to run
    processes = [mp.Process(target=multiproc,
                            args=(nthreads, 120, threading.Lock()))
                 for x in range(nprocesses)]

    # run processes
    for p in processes:
        p.start()

    # exit the completed processes
    for p in processes:
        p.join()

    # kill the process which collect statistics in background
    #os.kill(int(stats_pid), signal.SIGKILL)
