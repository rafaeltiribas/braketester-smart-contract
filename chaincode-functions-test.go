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

func main() {
	reportData := readFile()                                      // Reading all data from the report and storing into this array.
	numWheels := len(reportData) / 2                              // Number of wheels of the vehicle.
	numAxle := numWheels / 2                                      // Number of axles from the vehicle.
	vehicleMass := calcMass(reportData, numWheels)                // Mass of the vehicle in kilograms.
	imbalanceApproval := approvesImbalance(reportData, numWheels) // Stores the approval status of breaking force imbalance of each axle.

	// Testing with prints.
	imbalance := calcImbalance(reportData[4], reportData[5])
	fmt.Println(reportData)
	fmt.Println(numAxle)
	fmt.Println(vehicleMass)
	fmt.Println(imbalance)
	fmt.Println(imbalanceApproval)
}
