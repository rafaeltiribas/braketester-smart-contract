/////////////////////////////////////////////
//    THE BLOCKCHAIN PKI EXPERIMENT     ////
///////////////////////////////////////////
/*
	This is the fabpki, a chaincode that implements a Public Key Infrastructure (PKI)
	for measuring instruments. It runs in Hyperledger Fabric 1.4.
	He was created as part of the PKI Experiment. You can invoke its methods
	to store measuring instruments public keys in the ledger, and also to verify
	digital signatures that are supposed to come from these instruments.

	@author: Wilson S. Melo Jr.
	@date: Oct/2019
*/
package main

import (
	//the majority of the imports are trivial...
	"bytes"
	"crypto/ecdsa"
	"crypto/x509"
	"encoding/json"
	"encoding/pem"
	"fmt"
	"math/big"
	"strconv"
	"time"
	"strings"

	//these imports are for Hyperledger Fabric interface
	"github.com/hyperledger/fabric-chaincode-go/shim"
	sc "github.com/hyperledger/fabric-protos-go/peer"
)

/* All the following functions are used to implement fabpki chaincode. This chaincode
basically works with 2 main features:
	1) A Register Authority RA (e.g., Inmetro) verifies a new measuring instrument (MI) and attests
	the correspondence between the MI's private key and public key. After doing this, the RA
	inserts the public key into the ledger, associating it with the respective instrument ID.

	2) Any client can ask for a digital signature ckeck. The client informs the MI ID, an
	information piece (usually a legally relevant register) and its supposed digital signature.
	The chaincode retrieves the MI public key and validates de digital signature.
*/

// SmartContract defines the chaincode base structure. All the methods are implemented to
// return a SmartContrac type.
type SmartContract struct {
}

// ECDSASignature represents the two mathematical components of an ECDSA signature once
// decomposed.
type ECDSASignature struct {
	R, S *big.Int
}

// Meter constitutes our key|value struct (digital asset) and implements a single
// record to manage the
// meter public key and measures. All blockchain transactions operates with this type.
// IMPORTANT: all the field names must start with upper case
type Meter struct {
	Vehicle        string `json:"vehicle"`
	ImbalanceApv   []bool `json:"imbalanceapproval"`
	PbApv          bool   `json:"parkbrakeapproval"`
	OvrlApv        bool   `json:"ovrleffiencyapproval"`
}


/*
//PubKey ecdsa.PublicKey `json:"pubkey"`
	Vehicle Plate string `json:"pubkey"`
	imbalanceApv []bool `json: "imbalanceapproval"`
	pbApv bool `json: "parkbrakeapproval"`
	ovrlApv bool `json: "ovrleffiencyapproval"`
*/

// PublicKeyDecodePEM method decodes a PEM format public key. So the smart contract can lead
// with it, store in the blockchain, or even verify a signature.
// - pemEncodedPub - A PEM-format public key
func PublicKeyDecodePEM(pemEncodedPub string) ecdsa.PublicKey {
	blockPub, _ := pem.Decode([]byte(pemEncodedPub))
	x509EncodedPub := blockPub.Bytes
	genericPublicKey, _ := x509.ParsePKIXPublicKey(x509EncodedPub)
	publicKey := genericPublicKey.(*ecdsa.PublicKey)

	return *publicKey
}

// Init method is called when the fabpki is instantiated.
// Best practice is to have any Ledger initialization in separate function.
// Note that chaincode upgrade also calls this function to reset
// or to migrate data, so be careful to avoid a scenario where you
// inadvertently clobber your ledger's data!
func (s *SmartContract) Init(stub shim.ChaincodeStubInterface) sc.Response {
	return shim.Success(nil)
}

// Invoke function is called on each transaction invoking the chaincode. It
// follows a structure of switching calls, so each valid feature need to
// have a proper entry-point.
func (s *SmartContract) Invoke(stub shim.ChaincodeStubInterface) sc.Response {
	// extract the function name and args from the transaction proposal
	fn, args := stub.GetFunctionAndParameters()

	//implements a switch for each acceptable function
	if fn == "registerMeter" {
		//registers a new meter into the ledger
		return s.registerMeter(stub, args)
	} else if fn == "sleepTest" {
		//retrieves the accumulated consumption
		return s.sleepTest(stub, args)

	} else if fn == "countHistory" {
		//look for a specific fill up record and brings its changing history
		return s.countHistory(stub, args)

	} else if fn == "countLedger" {
		//look for a specific fill up record and brings its changing history
		return s.countLedger(stub)

	} else if fn == "queryLedger" {
		//execute a CouchDB query, args must include query expression
		return s.queryLedger(stub, args)
	}

	//function fn not implemented, notify error
	return shim.Error("Chaincode does not support this function.")
}

/*
	SmartContract::registerMeter(...)
	Does the register of a new meter into the ledger.
	The meter is the base of the key|value structure.
	The key constitutes the meter ID.
	- args[0] - meter ID
	- args[1] - the public key associated with the meter
*/

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

func  intTest(num int) int{
	return num + 1
}

func (s *SmartContract) registerMeter(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	//gets the parameters associated with the meter ID and the public key (in PEM format)
	// meterid := args[0]
	// strpubkey := args[1]
	// data, err := strconv.Atoi(fileScanner.Text())
	//////////////////////////////////////////////////////////////////////////////////////
	
	/*
		Solução: Carregar a string para uma variável do tipo .json
		*usar dicionário* 
	// dev-peer0.inmetro.br-braketester_1.0-59e7064dffb5f8f95aeb965ef848200e7f213dbd633970887d5fd766d2a5485d-3db8b4e2ac3ef010997212f9cf5c74eee50be5e1aee9b15edf44e2d0afe1c867
	*/
	//adicionar if para verificacao de parametros
	fmt.Println("TESTE1")

	vehicle_plate := args[0]
	jsonString := args[1]
	
	fmt.Println("TESTE2")
	
	fmt.Println(jsonString)
	jsonString = strings.ReplaceAll(jsonString, "'", "\"")
	fmt.Println(jsonString)

        var dataMap map[string][]string
        err := json.Unmarshal([]byte(jsonString), &dataMap)
        if err != nil {
            fmt.Println("Erro ao decodificar JSON:", err)
        }
        dataStr := dataMap["data"]
        reportData := make([]int, len(dataStr))
        for i, valStr := range dataStr {
            val, err := strconv.Atoi(valStr)
            if err != nil {
                fmt.Println("Erro ao converter valor para inteiro:", err)
            }
            reportData[i] = val
        }
	
    	fmt.Println("TESTE4")
    	fmt.Println(reportData)
	
	/*
	for i := 0; i < len(fileData)-1; i++{
		fileValue, err := strconv.Atoi(fileData[i])
		if err != nil {
			log.Fatal(err)
		}
		reportData = append(reportData, fileValue)
	}*/

	fmt.Println("TESTE5")
	
	pbTotalForce := reportData[len(reportData)-1]
	numWheels := (len(reportData)-1) / 2 
	fmt.Println(len(reportData))
	fmt.Println(numWheels)
	fmt.Println("TESTE6")
	
	vehicleWeight := calcTotalWeight(reportData, numWheels) 
	fmt.Println("Passou calcTotalWeight")
	vehicleMass := calcMass(vehicleWeight) 
	fmt.Println("Passou calcMass")
	vehicleType := checkType(vehicleMass)
	fmt.Println("Passou checkType")
	imbalanceApproval := approvesImbalance(reportData, numWheels) 
	fmt.Println("Passou approvesImbalance")
	pbApproval := approvesPbEfficiency(calcPbEfficiency(pbTotalForce, vehicleWeight))
	fmt.Println("Passou approvesPbEfficiency")
	ovrlEfficiencyApproval := approvesOvrlEfficiency(reportData, vehicleType)
	fmt.Println("Passou approvesOvrlEfficiency")
	
	fmt.Println("TESTE7")
	
	///////////////////////////////////////////////////////////////////////////////////////
	
	//creates the meter record with the respective public key
	var meter = Meter{ImbalanceApv: imbalanceApproval, PbApv: pbApproval, OvrlApv: ovrlEfficiencyApproval}
	
	fmt.Println("TESTE8")

	//encapsulates meter in a JSON structure
	meterAsBytes, _ := json.Marshal(meter)
	
	fmt.Println("TESTE9")

	//registers meter in the ledger
	stub.PutState(vehicle_plate, meterAsBytes)
	
	fmt.Println("TESTE10")

	//loging...
	fmt.Println("Registering meter: ", meter)
	
	fmt.Println("FIM")

	//notify procedure success
	return shim.Success(nil)
	
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*
	This method is a dummy test that makes the endorser "sleep" for some seconds.
	It is usefull to check either the sleeptime affects the performance of concurrent
	transactions.
	- args[0] - sleeptime (in seconds)
*/
func (s *SmartContract) sleepTest(stub shim.ChaincodeStubInterface, args []string) sc.Response {
	//validate args vector lenght
	if len(args) != 1 {
		return shim.Error("It was expected 1 parameter: <sleeptime>")
	}

	//gets the parameter associated with the meter ID and the incremental measurement
	sleeptime, err := strconv.Atoi(args[0])

	//test if we receive a valid meter ID
	if err != nil {
		return shim.Error("Error on retrieving sleep time")
	}

	//tests if sleeptime is a valid value
	if sleeptime > 0 {
		//stops during sleeptime seconds
		time.Sleep(time.Duration(sleeptime) * time.Second)
	}

	//return payload with bytes related to the meter state
	return shim.Success(nil)
}

/*
   This method brings the changing history of a specific meter asset. It can be useful to
   query all the changes that happened with a meter value.
   - args[0] - asset key (or meter ID)
*/
func (s *SmartContract) queryHistory(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	//validate args vector lenght
	if len(args) != 1 {
		return shim.Error("It was expected 1 parameter: <key>")
	}

	historyIer, err := stub.GetHistoryForKey(args[0])

	//verifies if the history exists
	if err != nil {
		//fmt.Println(errMsg)
		return shim.Error("Fail on getting ledger history")
	}

	// buffer is a JSON array containing records
	var buffer bytes.Buffer
	var counter = 0
	buffer.WriteString("[")
	bArrayMemberAlreadyWritten := false
	for historyIer.HasNext() {
		//increments iterator
		queryResponse, err := historyIer.Next()
		if err != nil {
			return shim.Error(err.Error())
		}
		// Add a comma before array members, suppress it for the first array member
		if bArrayMemberAlreadyWritten == true {
			buffer.WriteString(",")
		}

		//generates a formated result
		buffer.WriteString("{\"Value\":")
		buffer.WriteString("\"")
		// Record is a JSON object, so we write as-is
		buffer.WriteString(string(queryResponse.Value))
		buffer.WriteString("\"")
		buffer.WriteString(", \"Counter\":")
		buffer.WriteString(strconv.Itoa(counter))
		//buffer.WriteString(queryResponse.Timestamp)
		buffer.WriteString("}")
		bArrayMemberAlreadyWritten = true

		//increases counter
		counter++
	}
	buffer.WriteString("]")
	historyIer.Close()

	//loging...
	fmt.Printf("Consulting ledger history, found %d\n records", counter)

	//notify procedure success
	return shim.Success(buffer.Bytes())
}

/*
   This method brings the number of times that a meter asset was modified in the ledger.
   It performs faster than queryHistory() method once it does not retrive any information,
   it only counts the changes.
   - args[0] - asset key (or meter ID)
*/
func (s *SmartContract) countHistory(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	//validate args vector lenght
	if len(args) != 1 {
		return shim.Error("It was expected 1 parameter: <key>")
	}

	historyIer, err := stub.GetHistoryForKey(args[0])

	//verifies if the history exists
	if err != nil {
		//fmt.Println(errMsg)
		return shim.Error("Fail on getting ledger history")
	}

	//creates a counter
	var counter int64
	counter = 0

	for historyIer.HasNext() {
		//increments iterator
		_, err := historyIer.Next()
		if err != nil {
			return shim.Error(err.Error())
		}

		//increases counter
		counter++

		fmt.Printf("Consulting ledger history, found %d\n records", counter)
	}
	// buffer is a JSON array containing records
	var buffer bytes.Buffer
	buffer.WriteString("[")
	buffer.WriteString("\"Counter\":")
	buffer.WriteString(strconv.FormatInt(counter, 10))
	buffer.WriteString("]")

	historyIer.Close()

	//loging...
	fmt.Printf("Consulting ledger history, found %d\n records", counter)

	//notify procedure success
	return shim.Success(buffer.Bytes())
}

/*
   This method counts the total of well succeeded transactions in the ledger.
*/
func (s *SmartContract) countLedger(stub shim.ChaincodeStubInterface) sc.Response {

	//use a range of keys, assuming that the max key value is 999999,
	resultsIterator, err := stub.GetStateByRange("0", "999999")
	if err != nil {
		return shim.Error(err.Error())
	}

	//defer iterator closes at the end of the function
	defer resultsIterator.Close()

	//creates a counter
	var counter int64
	var keys int64
	counter = 0
	keys = 0

	//the interator checks all the valid keys
	for resultsIterator.HasNext() {

		//increments iterator
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return shim.Error(err.Error())
		}

		//busca historico da proxima key
		historyIer, err := stub.GetHistoryForKey(queryResponse.Key)

		//verifies if the history exists
		if err != nil {
			//fmt.Println(errMsg)
			return shim.Error(err.Error())
		}

		defer historyIer.Close()

		for historyIer.HasNext() {
			//increments iterator
			_, err := historyIer.Next()
			if err != nil {
				return shim.Error(err.Error())
			}

			//increases counter
			counter++
		}
		fmt.Printf("Consulting ledger history, found key %s\n", queryResponse.Key)

		keys++
	}
	// buffer is a JSON array containing records
	var buffer bytes.Buffer
	buffer.WriteString("[")
	buffer.WriteString("\"Counter\":")
	buffer.WriteString(strconv.FormatInt(counter, 10))
	buffer.WriteString("\"Keys\":")
	buffer.WriteString(strconv.FormatInt(keys, 10))
	buffer.WriteString("]")

	//loging...
	fmt.Printf("Consulting ledger history, found %d transactions in %d keys\n", counter, keys)

	//notify procedure success
	return shim.Success(buffer.Bytes())
}

/*
   This method executes a free query on the ledger, returning a vector of meter assets.
   The query string must be a query expression supported by CouchDB servers.
   - args[0] - query string.
*/
func (s *SmartContract) queryLedger(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	//validate args vector lenght
	if len(args) != 1 {
		return shim.Error("It was expected 1 parameter: <query string>")
	}

	//using auxiliar variable
	queryString := args[0]

	//loging...
	fmt.Printf("Executing the following query: %s\n", queryString)

	//try to execute query and obtain records iterator
	resultsIterator, err := stub.GetQueryResult(queryString)
	//test if iterator is valid
	if err != nil {
		return shim.Error(err.Error())
	}
	//defer iterator closes at the end of the function
	defer resultsIterator.Close()

	// buffer is a JSON array containing QueryRecords
	var buffer bytes.Buffer
	buffer.WriteString("[")
	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		//increments iterator
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return shim.Error(err.Error())
		}
		// Add a comma before array members, suppress it for the first array member
		if bArrayMemberAlreadyWritten == true {
			buffer.WriteString(",")
		}

		//generates a formated result
		buffer.WriteString("{\"Key\":")
		buffer.WriteString("\"")
		buffer.WriteString(queryResponse.Key)
		buffer.WriteString("\"")
		buffer.WriteString(", \"Record\":")
		// Record is a JSON object, so we write as-is
		buffer.WriteString(string(queryResponse.Value))
		buffer.WriteString("}")
		bArrayMemberAlreadyWritten = true
	}
	buffer.WriteString("]")

	//loging...
	fmt.Printf("Obtained the following fill up records: %s\n", buffer.String())

	//notify procedure success
	return shim.Success(buffer.Bytes())
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////

// Calculates the mass of a vehicle using weight values from report.
func calcMass(weightSum int) float64 {
	gvtAcceleration := 9.8
	return float64(weightSum) / gvtAcceleration
}

// Sums the weight values and returns the total result.
func calcTotalWeight(reportData []int, numWheels int) int {
	var weightSum int
	for i := 0; i < numWheels; i++ {
		weightSum += reportData[i]
	}
	return weightSum
}

// Checking the type of a vehicle by its mass.
func checkType(vehicleMass float64) bool {
	var vehicleType bool
	if vehicleMass > 3500 {
		vehicleType = true // True stands for heavy weight vehicle.
	} else {
		vehicleType = false // False stands for light weight vehicle.
	}
	return vehicleType
}

// Calculates the braking force imbalance from two wheels.
func calcImbalance(leftWheel int, rightWheel int) float64 {
	var higherNum int
	var lowerNum int
	if leftWheel > rightWheel {
		higherNum = leftWheel
		lowerNum = rightWheel
	} else {
		higherNum = rightWheel
		lowerNum = leftWheel
	}
	imbalance := 100 * (float64(higherNum-lowerNum) / float64(higherNum))
	return imbalance
}

// Check if the braking force of each axle is approved or not.
func approvesImbalance(reportData []int, numWheels int) []bool {
	var approvalStatus []bool
	for i := numWheels; i < (len(reportData)-2); i += 2 {
		if calcImbalance(reportData[i], reportData[i+1]) <= 20 {
			approvalStatus = append(approvalStatus, true)
		} else {
			approvalStatus = append(approvalStatus, false)
		}
	}
	return approvalStatus
}

// Calculates overall braking efficiency
func calcOvrlEfficiency(reportData []int) float64 {
	var overallEfficiency, weightSum, brakingFrcSum float64
	for i := 0; i < len(reportData); i++ {
		if i < (len(reportData)-1)/2 {
			weightSum += float64(reportData[i])
		} else {
			brakingFrcSum += float64(reportData[i])
		}
	}
	overallEfficiency = weightSum / brakingFrcSum
	return 100 * overallEfficiency
}

// Calculates the parking braker efficiency.
func calcPbEfficiency(totalForce int, totalWeight int) float64 {
	return 100 * (float64(totalForce) / float64(totalWeight))
}

// Check if parking braker efficiency is approved or not.
func approvesPbEfficiency(pbEfficiency float64) bool {
	if pbEfficiency >= 18 {
		return true
	} else {
		return false
	}
}

// Check if overall braking efficiency is approved or not.
func approvesOvrlEfficiency(reportData []int, vehicleType bool) bool {
	if vehicleType == true { // Heavy vehicle
		if calcOvrlEfficiency(reportData) >= 50 {
			return true
		} else {
			return false
		}
	} else { // Light vehicle
		if calcOvrlEfficiency(reportData) >= 55 {
			return true
		} else {
			return false
		}
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////


/*
 * The main function starts up the chaincode in the container during instantiate
 */
func main() {

	////////////////////////////////////////////////////////
	// USE THIS BLOCK TO COMPILE THE CHAINCODE
	if err := shim.Start(new(SmartContract)); err != nil {
		fmt.Printf("Error starting SmartContract chaincode: %s\n", err)
	}
	////////////////////////////////////////////////////////

	////////////////////////////////////////////////////////
	// USE THIS BLOCK TO PERFORM ANY TEST WITH THE CHAINCODE

	// //create pair of keys
	// privateKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	// if err != nil {
	// 	panic(err)
	// }

	// //marshal the keys in a buffer
	// e, err := json.Marshal(privateKey)
	// if err != nil {
	// 	fmt.Println(err)
	// 	return
	// }

	// _ = ioutil.WriteFile("ecdsa-keys.json", e, 0644)

	// //read the saved key
	// file, _ := ioutil.ReadFile("ecdsa-keys.json")

	// myPrivKey := ecdsa.PrivateKey{}
	// //myPubKey := ecdsa.PublicKey{}

	// _ = json.Unmarshal([]byte(file), &myPrivKey)

	// fmt.Println("Essa é minha chave privada:")
	// fmt.Println(myPrivKey)

	// myPubKey := myPrivKey.PublicKey

	// //test digital signature verifying
	// msg := "message"
	// hash := sha256.Sum256([]byte(msg))
	// fmt.Println("hash: ", hash)

	// r, s, err := ecdsa.Sign(rand.Reader, privateKey, hash[:])
	// if err != nil {
	// 	panic(err)
	// }
	// fmt.Printf("signature: (0x%x, 0x%x)\n", r, s)

	// myPubKey.Curve = elliptic.P256()

	// fmt.Println("Essa é minha chave publica:")
	// fmt.Println(myPubKey)

	// valid := ecdsa.Verify(&myPubKey, hash[:], r, s)
	// fmt.Println("signature verified:", valid)

	// otherpk := "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE6NXETwtkAKGWBcIsI6/OYE0EwsVj\n3Fc4hHTaReNfq6Hz2UEzsJKCYN0stjPCXbpdUlYtETC1a3EcS3SUVYX6qA==\n-----END PUBLIC KEY-----\n"

	// newkey := PublicKeyDecodePEM(otherpk)
	// myPubKey.Curve = elliptic.P256()

	// //valid = ecdsa.Verify(newkey, hash[:], r, s)
	// //fmt.Println("signature verified:", valid)

	// mysign := "MEYCIQCY16jbdY222oEpFiSRwXPi1kS7c4wuwxYXeWJOoAjnVgIhAJQTM+itbm1mQyd40Ug0xr2/AvjZmFSdoc/iSSHA6nRI"

	// // first decode the signature to extract the DER-encoded byte string
	// der, err := base64.StdEncoding.DecodeString(mysign)
	// if err != nil {
	// 	panic(err)
	// }

	// // unmarshal the R and S components of the ASN.1-encoded signature into our
	// // signature data structure
	// sig := &ECDSASignature{}
	// _, err = asn1.Unmarshal(der, sig)
	// if err != nil {
	// 	panic(err)
	// }

	// valid = ecdsa.Verify(&newkey, hash[:], sig.R, sig.S)
	// fmt.Println("signature verified:", valid)

	// fmt.Println("Curve: ", newkey.Curve.Params())

	////////////////////////////////////////////////////////

}

