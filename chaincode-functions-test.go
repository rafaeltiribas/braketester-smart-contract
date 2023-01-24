package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strconv"
)

// A function that reads all lines from the .txt file and return an array of integers with them.
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

func main() {
	reportData := readFile() // Reading all data from the report and storing into this array.
	fmt.Println(reportData)
}
