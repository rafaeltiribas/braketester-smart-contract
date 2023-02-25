import binascii
import hashlib
import json
import random
from hfc.fabric import Client as client_fabric
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

from pandas.core.window import doc

# For convencion, the first domain should be your admin domain.
domain = ["inmetro.br", "nesa.br"]
channel_name = "nmi-channel"
cc_name = "nesa"
cc_version = "1.0"
callpeer = []

f = open('2022-06-24_13_18_33_signal_2Sensors.json')
signal = json.load(f)
signal = json.dumps(signal)

def insertLSH(signal):

    data = json.loads(signal)

    for sensor in range(len(data['signals'])):

        id = data['hardware_id'] + data['signals'][sensor]['sensor_id']
        print(id)
        signal_data = data['signals'][sensor]['signal_data']

        shingles = shingle_doc(signal_data)
        
        hash_lsh = lsh(shingles)

        hash_crip = hash_256(shingles)

        Sensor_data = {
            'timestamp_signal': data['timestamp_signal'],
            'sampling_period_in_sec': data['signals'][sensor]['sampling_period_in_sec'],
            'overall_samples:': data['signals'][sensor]['overall_samples:'],
            'sample_rate_hz': data['signals'][sensor]['sample_rate_hz'],
            'total_of_seconds': data['signals'][sensor]['total_of_seconds'],
            'signal_data': signal_data,
            'hash_lsh': str(hash_lsh),
            'hash_crip': str(hash_crip)
        }

        Sensor_data = json.dumps(Sensor_data, indent=2).encode('UTF-8')
        loop = asyncio.get_event_loop()
        # instantiate the hyperledeger fabric client
        c_hlf = client_fabric(net_profile=("inmetro.br.json"))

        # get access to Fabric as Admin user
        admin = c_hlf.get_user(domain[0], 'Admin')

        for i in domain:
            callpeer.append("peer0." + i)

        # the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
        c_hlf.new_channel(channel_name)
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
        # invoke the chaincode to register the meter
        response = loop.run_until_complete(c_hlf.chaincode_invoke(
            requestor=admin,
            channel_name='nmi-channel',
            peers=['peer0.inmetro.br'],
            args=[id, Sensor_data],
            cc_name=cc_name,
            fcn='insertMeasurementLSH'
        ))

        return "Sucess"

def shingle_doc(signal_data):
    docsAsShingleSets = {}

    disallowed_characters = "[]\n,"

    series = ""

    series = str(signal_data)
    series = series.replace("][", " ")
    for j in disallowed_characters:
        series = series.replace(j, "")
    words = series.split(" ")

    shinglesInDoc = set()

    # For each word in the document...
    for index in range(0, len(words) - 2):
        # Construct the shingle text by combining three words together.
        shingle = words[index] + " " + words[index + 1] + " " + words[index + 2]
        shingle = str.encode(shingle)

        # Hash the shingle to a 32-bit integer.
        crc = binascii.crc32(shingle)

        # Add the hash value to the list of shingles for the current document.
        # Note that set objects will only add the value to the set if the set
        # doesn't already contain it.
        shinglesInDoc.add(crc)

    # Store the completed list of shingles for this document in the dictionary.
    docsAsShingleSets = list(shinglesInDoc)
    
    return docsAsShingleSets

def hash_256(shingles):
    shingles = str(shingles)
    hash_crip = hashlib.sha256(b"shingles")
    hash_crip = hash_crip.hexdigest()
    return hash_crip

def lsh(shingles):
    
    # This is the number of components in the resulting MinHash signatures.
    # Correspondingly, it is also the number of random hash functions that
    # we will need in order to calculate the MinHash.
    numHashes = 20

    # Time this step.

    print('\nGenerating random hash functions...')

    # Record the maximum shingle ID that we assigned.
    maxShingleID = 2**32-1

    # We need the next largest prime number above 'maxShingleID'.
    # I looked this value up here: 
    # http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php
    nextPrime = 4294967311

    # Our random hash function will take the form of:
    #   h(x) = (a*x + b) % c
    # Where 'x' is the input value, 'a' and 'b' are random coefficients, and 'c' is
    # a prime number just greater than maxShingleID.

    # Generate a list of 'k' random coefficients for the random hash functions,
    # while ensuring that the same value does not appear multiple times in the 
    # list
    
    # For each of the 'numHashes' hash functions, generate a different coefficient 'a' and 'b'.   
    coeffA = pickRandomCoeffs(numHashes)
    
    coeffB = pickRandomCoeffs(numHashes)
    
    print('\nGenerating MinHash signatures for all documents...')

    # List of documents represented as signature vectors
    signatures = []

    # Rather than generating a random permutation of all possible shingles, 
    # we'll just hash the IDs of the shingles that are *actually in the document*,
    # then take the lowest resulting hash code value. This corresponds to the index 
    # of the first shingle that you would have encountered in the random order.
    # The resulting minhash signature for this document. 
    signature = []
    
    # For each of the random hash functions...
    for i in range(0, numHashes):
        
        
        # For each of the shingles actually in the document, calculate its hash code
        # using hash function 'i'. 
        
        # Track the lowest hash ID seen. Initialize 'minHashCode' to be greater than
        # the maximum possible value output by the hash.
        minHashCode = nextPrime + 1
        # For each shingle in the document...
        for shingleID in shingles:
        # Evaluate the hash function.

            hashCode = (coeffA[i] * shingleID + coeffB[i]) % nextPrime 
        
        # Track the lowest hash code seen.
            if hashCode < minHashCode:
                minHashCode = hashCode

        # Add the smallest hash code value as component number 'i' of the signature.
        signature.append(minHashCode)
    
    # Store the MinHash signature for this document.
    signatures.append(signature)

    return signatures[0]

def pickRandomCoeffs(k):

    # Record the maximum shingle ID that we assigned.
    maxShingleID = 2**32-1
    # Create a list of 'k' random values.
    randList = []
    
    while k > 0:
    
        # Get a random shingle ID.
        randIndex = random.randint(0, maxShingleID) 
  
    # Ensure that each random number is unique.
        while randIndex in randList:
            randIndex = random.randint(0, maxShingleID) 
    
        # Add the random number to the list.
        randList.append(randIndex)
        k = k - 1
    
    return randList

insertLSH(signal)