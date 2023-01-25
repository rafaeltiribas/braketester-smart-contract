<h1 align="center">
📄<br>  frenometer-smart-contract
</h1>

## chaincode-functions-test.go

> This file contains a scratch for the chaincode functions. He reads a report("report-data.csv") and with its values implements a number of functions to write a new report for the vehicle braking inspection approval.

## report-data.csv

> A file with all data from the frenometer report. It follows a strict rule: the first values must be the weight measured in each wheel. It starts with the first axle left-side weight value, then the right-side and goes to the next axle. The vehicle can contain as many axis as it wants. Only after all weight values written it writes the braking forces, following the same algorithm as before.

## report-approval.csv

> The report generated by chaincode-functions-test.go file. It contains the type of the vehicle(heavy or light weight), each axle braking imbalance approval status and the overall breaking efficiency approval status.
