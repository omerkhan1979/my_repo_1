package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/knadh/koanf"
)

type jenkinsRunResponse struct {
	Result      string
	Building    bool
	DisplayName string
}

type jenkinsJobResponse struct {
	LastBuild jenkinsBuild
}

type jenkinsBuild struct {
	Number int
	Url    string
}

func generateJenkinsDeployJobUrlMultiDeployPipeline(client, env string, clientK *koanf.Koanf) string {
	jenkinsJobURL := fmt.Sprintf("%s/job/multi_deploy_pipeline/buildWithParameters?CLIENT=%s&ENV=%s", JENKINS_URL, client, env)
	jenkinsJobURL += generateServiceVersionsQueryString(clientK)
	return jenkinsJobURL
}

func triggerJenkinsMultiPipelineDeployJob(client, env string, clientK *koanf.Koanf) error {
	jenkinsJobURL := generateJenkinsDeployJobUrlMultiDeployPipeline(client, env, clientK)
	err := triggerJenkinsJob(jenkinsJobURL)
	if err != nil {
		return err
	}
	return nil
}

func getFromJenkins(url string) ([]byte, error) {
	value, exist := os.LookupEnv("JENKINS_PASSWORD")
	if !exist {
		return nil, errors.New("JENKINS_PASSWORD is not set!")
	}
	jenkinsPassword := value
	httpClient := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.SetBasicAuth(JENKINS_USER, jenkinsPassword)
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	return body, nil
}

func getJobs(count int) ([]int, error) {
	url := fmt.Sprintf("%s/job/multi_deploy_pipeline/api/json", JENKINS_URL)
	body, err := getFromJenkins(url)
	if err != nil {
		return nil, err
	}
	var recent jenkinsJobResponse
	err = json.Unmarshal(body, &recent)
	if err != nil {
		fmt.Println(string(body))
		return nil, err
	}
	jobs := make([]int, 0)

	for i := 1; i <= count; i++ {
		jobs = append(jobs, recent.LastBuild.Number+i)
	}
	return jobs, nil
}

func followDeployJob(pipelineID int, responses chan jenkinsRunResponse, wg *sync.WaitGroup) {
	defer wg.Done()
	url := fmt.Sprintf("%s/job/multi_deploy_pipeline/%d/api/json", JENKINS_URL, pipelineID)
	fmt.Println(url)
	time.Sleep(time.Second * 600)

	var json_resp jenkinsRunResponse
	failedJenkinsCallCounter := 0
	failedJSONCounter := 0

	running := true
	for running {
		body, err := getFromJenkins(url)
		if err != nil {
			// In order for the script to make it to this point, it must be able to connect to jenkins
			// A failure here may be indicative of a transient network error.
			// Retry the the call a few times, if there are more than 3 getFromJenkins failures in a row, then return.
			fmt.Printf("Failed to query jenkins at: %s\n", url)
			fmt.Println(err)
			if failedJenkinsCallCounter > 3 {
				responses <- json_resp
				return
			} else {
				failedJenkinsCallCounter += 1
			}
		} else {
			failedJenkinsCallCounter = 0
		}

		err = json.Unmarshal(body, &json_resp)
		if err != nil {
			// Assume that if the unmarshal returns an error, there was some form of problem with jenkin's api response.
			// Retry the the call a few times, if there are more than 3 json unmarshal failures in a row, then return.
			fmt.Printf("Failed to Read json data from jenkins response for pipeline %d\n", pipelineID)
			fmt.Println(err)
			if failedJSONCounter > 3 {
				responses <- json_resp
				return
			} else {
				failedJSONCounter += 1
			}
		} else {
			failedJSONCounter = 0
		}
		running = json_resp.Building
		if running {
			time.Sleep(time.Second * 5)
		}
	}
	responses <- json_resp
}

// Trigger RTDAT (not passing service_versions)
// Don't need 'env'.  RTDAT's JenkinsFile contains the logic, and we only ever run against QAI)
func triggerJenkinsReleaseTrainDeployAndTestJob(clients []string, k *koanf.Koanf, RT string, oktaToken string) error {

	//Build client query string portion of the URL
	clientsQueryString := ""
	for _, client := range clients {
		fmt.Println("client: " + client)
		clientsQueryString += fmt.Sprintf("&CLIENT_%s=true", client)
	}
	serviceVersionsQueryString := generateServiceVersionsQueryString(k)
	serviceVersionsQueryString = strings.Replace(serviceVersionsQueryString, "TAKEOFF_platform_kubernetes", "platform", 1)  //PROD-2002
	date := strings.Split(time.Now().String(), " ")[0]  //Has to be an easier way to get the date??
	testRunName := fmt.Sprintf("TESTRUN_NAME=[%s]+RTM+RTDAT:+%s", date, RT)

	jenkinsJobURL := fmt.Sprintf("%s/job/Tests/job/ReleaseTrainDeployAndTest/buildWithParameters?%s%s%s%s",
		JENKINS_URL, testRunName, clientsQueryString, serviceVersionsQueryString, oktaToken)

	err := triggerJenkinsJob(jenkinsJobURL)
	if err != nil {
		return err
	}
	return nil
}

func generateServiceVersionsQueryString (thisK *koanf.Koanf) string {
	serviceVersionsQueryString := ""
	// // loop via keys map to find the service object
	for _, value := range thisK.KeyMap() {
		// the parent object will have length equal 1
		if len(value) == 1 {
			service := value[0]
			helm_chart_version_key := fmt.Sprintf("%s.helm_chart_version", service)
			helm_chart_version := thisK.String(helm_chart_version_key)

			underscoredSvc := strings.Replace(service, "-", "_", -1)
			if service == "platform" {
				serviceVersionsQueryString += fmt.Sprintf("&TAKEOFF_%s_kubernetes=%s", underscoredSvc, helm_chart_version)
			} else {
				serviceVersionsQueryString += fmt.Sprintf("&TAKEOFF_%s=%s", underscoredSvc, helm_chart_version)
			}
		}
	}
	return serviceVersionsQueryString
}
