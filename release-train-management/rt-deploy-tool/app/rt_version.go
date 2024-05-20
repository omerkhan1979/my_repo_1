package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func getLatestReleaseTrainVersion() (string, error) {
	file, err := os.Open(RELEASE_TRAINS_FILE)
	if err != nil {
		return "", err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var last []byte
	for scanner.Scan() {
		last = scanner.Bytes()
	}
	if err := scanner.Err(); err != nil {
		return "", err
	}
	splittedString := strings.Split(fmt.Sprintf("%s", last), ":")
	RT := splittedString[0]
	return RT, nil
}

func getReleaseTrainVersion() (string, error) {
	var RT string
	var err error

	val, present := os.LookupEnv("RELEASE_TRAIN_VERSION")
	if (present && val != "") {
		RT = val
		fmt.Println("Release Train Version used -> Predefined, ", RT)
	} else {
		RT, err = getLatestReleaseTrainVersion()
		if err != nil {
			return "", err
		}
		fmt.Println("Release Train Version used -> Latest, ", RT)
	}
	return RT, nil
}
