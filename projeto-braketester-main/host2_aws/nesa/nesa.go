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
	"encoding/json"
	"fmt"
	"math/big"

	//these imports are for Hyperledger Fabric interface
	//"github.com/hyperledger/fabric/core/chaincode/shim"
	"github.com/hyperledger/fabric-chaincode-go/shim"
	//sc "github.com/hyperledger/fabric/protos/peer"
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
	//PubKey ecdsa.PublicKey `json:"pubkey"`
	PubKey string `json:"pubkey"`
}

type Data struct {
	Timestamp           string  `json:"timestamp"`
	Equip1           string  `json:"equip1"`
	Equip2           string  `json:"equip2"`
	Equip3           string  `json:"equip3"`
	Equip4           string  `json:"equip4"`		
}

type Data2 struct {
	Media		string  `json:"media"`
	Mediana		string  `json:"media"`
	DesvAmostral		string  `json:"desvAmostral"`
	Moda		string  `json:"moda"`
	Variancia		string  `json:"variancia"`
	Mad		string  `json:"mad"`
	
	Media2		string  `json:"media2"`
	Mediana2		string  `json:"media2"`
	DesvAmostral2		string  `json:"desvAmostral2"`
	Moda2		string  `json:"moda2"`
	Variancia2		string  `json:"variancia2"`
	Mad2		string  `json:"mad2"`
	
	Media3		string  `json:"media3"`
	Mediana3		string  `json:"media3"`
	DesvAmostral3		string  `json:"desvAmostral3"`
	Moda3		string  `json:"moda3"`
	Variancia3		string  `json:"variancia3"`
	Mad3		string  `json:"mad3"`
	
	Media4		string  `json:"media4"`
	Mediana4		string  `json:"media4"`
	DesvAmostral4		string  `json:"desvAmostral4"`
	Moda4		string  `json:"moda4"`
	Variancia4		string  `json:"variancia4"`
	Mad4		string  `json:"mad4"`
	
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
	if fn == "insertMeasurement" {
		//inserts a measurement which increases the meter consumption counter.
		return s.insertMeasurement(stub, args)

	} else if fn == "getConsumption" {
		//retrieves the accumulated consumption
		return s.getConsumption(stub, args)

	}

	//function fn not implemented, notify error
	return shim.Error("Chaincode does not support this function.")
}

func (s *SmartContract) insertMeasurement(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	//validate args vector lenght
	if len(args) != 2 {
		return shim.Error("It was expected 2 parameter: <meter ID> <measurement>")
	}

	//gets the parameter associated with the meter ID
	meterid := args[0]

	//try to convert the informed measurement into the format []byte, required by Gomorph
	measurement, err := json.Marshal(args[1])

	if err != nil {
		panic(err)
	}

	//check if we have success
	if measurement == nil {
		//measurement is not a proper number
		return shim.Error("Error on veryfing measurement, it is not a proper input, deu ruim")
	}

	//MyMeter := Data{}
	MyMeter := Data2{}

	//convert bytes into a Data object
	json.Unmarshal(measurement, &MyMeter)

	//update Data state in the ledger
	stub.PutState(meterid, measurement)

	//loging...
	fmt.Println("Updating Data consumption:", measurement)

	//notify procedure success
	return shim.Success(nil)
}

func (s *SmartContract) getConsumption(stub shim.ChaincodeStubInterface, args []string) sc.Response {
	//validate args vector lenght
	if len(args) != 1 {
		return shim.Error("It was expected 1 parameter: <meter ID>")
	}

	//gets the parameter associated with the meter ID and the incremental measurement
	meterid := args[0]

	//retrive Data record
	meterAsBytes, err := stub.GetState(meterid)

	MyMeter := Data{}
	
	json.Unmarshal(meterAsBytes, &MyMeter)

	//test if we receive a valid meter ID
	if err != nil || meterAsBytes == nil {
		return shim.Error("Error on retrieving meter ID register")
	}

	//return payload with bytes related to the meter state
	return shim.Success(meterAsBytes)
}

/*
	SmartContract::registerMeter(...)
	Does the register of a new meter into the ledger.
	The meter is the base of the key|value structure.
	The key constitutes the meter ID.
	- args[0] - meter ID
	- args[1] - the public key associated with the meter
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
