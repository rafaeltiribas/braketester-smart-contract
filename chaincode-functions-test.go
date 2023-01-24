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
func calcMass(reportData []int, numAxle int) float64 {
	var weightSum float64
	gvtAcceleration := 9.8
	for i := 0; i < numAxle; i++ {
		weightSum += float64(reportData[i])
	}
	mass := weightSum / gvtAcceleration
	return mass
}

func main() {
	reportData := readFile()                     // Reading all data from the report and storing into this array.
	numAxle := len(reportData) / 2               // Number of axes from the vehicle.
	vehicleMass := calcMass(reportData, numAxle) // Mass of the vehicle in kilograms.

	// Testing with prints.
	fmt.Println(reportData)
	fmt.Println(numAxle)
	fmt.Println(vehicleMass)
}
