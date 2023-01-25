package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strconv"
)

// A function that reads all lines from the .txt file and returns an array of integers with them.
func readFile() []int {
	file, err := os.Open("report-data.txt")
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
func calcMass(reportData []int, numWheels int) float64 {
	var weightSum float64
	gvtAcceleration := 9.8
	for i := 0; i < numWheels; i++ {
		weightSum += float64(reportData[i])
	}
	mass := weightSum / gvtAcceleration
	return mass
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
func approvesOvrlEfficiency(reportData []int) bool {
	if calcOvrlEfficiency(reportData) >= 55 {
		return true
	} else {
		return false
	}
}

func main() {
	reportData := readFile()                                      // Reading all data from the report and storing into this array.
	numWheels := len(reportData) / 2                              // Number of wheels of the vehicle.
	numAxle := numWheels / 2                                      // Number of axles from the vehicle.
	vehicleMass := calcMass(reportData, numWheels)                // Mass of the vehicle in kilograms.
	imbalanceApproval := approvesImbalance(reportData, numWheels) // Stores the approval status of breaking force imbalance of each axle.
	ovrlEfficiencyApproval := approvesOvrlEfficiency(reportData)  // Overall braking efficiency approval status.

	// Testing with prints.
	imbalance := calcImbalance(reportData[4], reportData[5])
	fmt.Println(reportData)
	fmt.Println(numAxle)
	fmt.Println(vehicleMass)
	fmt.Println(imbalance)
	fmt.Println(imbalanceApproval)
	fmt.Println(ovrlEfficiencyApproval)
}
