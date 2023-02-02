package main

import (
	"bufio"
	"log"
	"os"
	"strconv"
)

// A function that reads all lines from the .txt file and returns an array of integers with them.
func readFile() []int {
	file, err := os.Open("report-data.csv")
	if err != nil {
		log.Fatal(err)
	}
	fileScanner := bufio.NewScanner(file)
	fileScanner.Split(bufio.ScanLines)
	var values []int
	for fileScanner.Scan() {
		data, err := strconv.Atoi(fileScanner.Text())
		if err != nil {
			panic(err)
		}
		values = append(values, data)
	}
	file.Close()
	return values
}

// Calculates the mass of a vehicle using weight values from report.
func calcMass(weightSum int) float64 {
	gvtAcceleration := 9.8
	return float64(weightSum) / gvtAcceleration
}

// Sums the weight values and returns the total result.
func totalWeight(reportData []int, numWheels int) int {
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
	for i := numWheels; i < len(reportData); i += 2 {
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
		if i < len(reportData)/2 {
			weightSum += float64(reportData[i])
		} else {
			brakingFrcSum += float64(reportData[i])
		}
	}
	overallEfficiency = weightSum / brakingFrcSum
	return 100 * overallEfficiency
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

// Writes a report of the approvals.
func reportApproval(imbalanceApproval []bool, ovrlEfficiencyApproval bool, vehicleType bool) {
	file, err := os.Create("report-approval.csv")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	var str string
	if vehicleType == true {
		str = "[Heavy]"
	} else {
		str = "[Light]"
	}
	_, err2 := file.WriteString("Vehicle type => " + str + ".\n")
	if err2 != nil {
		log.Fatal(err2)
	}
	for i := 0; i < len(imbalanceApproval); i++ {
		if imbalanceApproval[i] == true {
			str = "[Approved]"
		} else {
			str = "[Disapproved]"
		}
		_, err := file.WriteString("Braking force imbalance of axis [" + strconv.Itoa(i+1) + "] was " + str + ".\n")

		if err != nil {
			log.Fatal(err)
		}
	}
	if ovrlEfficiencyApproval == true {
		str = "[Approved]"
	} else {
		str = "[Disapproved]"
	}
	_, err3 := file.WriteString("Total braking efficiency was " + str + ".\n")

	if err3 != nil {
		log.Fatal(err3)
	}

}

func main() {
	reportData := readFile()                                                  // Reading all data from the report and storing into this array.
	numWheels := len(reportData) / 2                                          // Number of wheels of the vehicle.
	vehicleMass := calcMass(totalWeight(reportData, numWheels))               // Mass of the vehicle in kilograms.
	vehicleType := checkType(vehicleMass)                                     // Indicates if a vehicle is light or heavy weighted.
	imbalanceApproval := approvesImbalance(reportData, numWheels)             // Stores the approval status of braking force imbalance of each axle.
	ovrlEfficiencyApproval := approvesOvrlEfficiency(reportData, vehicleType) // Overall braking efficiency approval status.
	reportApproval(imbalanceApproval, ovrlEfficiencyApproval, vehicleType)    // Writing a new report.

	// Testing variables with prints.
	// imbalance := calcImbalance(reportData[4], reportData[5])
	//fmt.Println(reportData)
	//fmt.Println(vehicleType)
	//fmt.Println(vehicleMass)
	//fmt.Println(imbalance)
	//fmt.Println(imbalanceApproval)
	//fmt.Println(ovrlEfficiencyApproval)
}
