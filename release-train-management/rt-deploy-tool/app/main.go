package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/knadh/koanf"
	"github.com/knadh/koanf/parsers/yaml"
	"github.com/knadh/koanf/providers/file"
)

var RELEASE_TRAINS_FILE = "ReleaseTrains.yaml"

var JENKINS_URL = "https://jenkins.tom.takeoff.com"
var JENKINS_USER = "takeoffbot@takeoff.com"

var k = koanf.New(".")

// Structure to unmarshal nested conf to.
// type ReleaseTrain struct {
// 	Version     string
// 	AuthService struct {
// 		helmChartVersion string `koanf:"helm_chart_version"`
// 	} `koanf:"auth-service"`
// }

func triggerJenkinsJob(JenkinsJobURL string) error {
	value, exist := os.LookupEnv("JENKINS_PASSWORD")
	if !exist {
		return errors.New("JENKINS_PASSWORD is not set!")
	}
	jenkinsPassword := value

	log.Println("Going to trigger Jenkins", JenkinsJobURL)
	httpClient := &http.Client{}
	req, err := http.NewRequest("POST", JenkinsJobURL, nil)
	if err != nil {
		return err
	}
	req.SetBasicAuth(JENKINS_USER, jenkinsPassword)

	resp, err := httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	// Print the output
	if resp.StatusCode >= 400 {
		return fmt.Errorf("request failed with error code: %d, and message: %s", resp.StatusCode, string(body))
	}
	log.Println("Status code:", resp.StatusCode)
	return nil
}

func readSliceFromFile(filename string) ([]string, error) {
	f, err := os.Open(filename)
	defer f.Close()
	if err != nil {
		return nil, err
	}
	rd := bufio.NewReader(f)
	slice := make([]string, 0)
	for {
		line, err := rd.ReadString('\n')
		if err == io.EOF {
			fmt.Print(line)
			break
		}
		if err != nil {
			return nil, err
		}
		// Github editor created ascii files with CRLF line endings
		// need to strip those out in the case of a file being created in that editor.
		line = strings.TrimSuffix(line, "\r\n")
		line = strings.TrimSuffix(line, "\n")
		slice = append(slice, line)
	}
	return slice, nil
}

func removeFromSlice(slice []string, item string) []string {
	for idx, val := range slice {
		if item == val {
			slice[idx] = slice[len(slice)-1] //replace blocked client with last client
			slice = slice[:len(slice)-1]     //drop the last client
			return slice
		}
	}
	return slice
}

func filterBlockedDeploy(filename string, clients []string, env string) ([]string, error) {
	fmt.Printf("ORIGINAL_CLIENTS_LIST=%s\n", strings.Join(clients, ","))
	blockDeployTo, err := readSliceFromFile(filename)
	if err != nil {
		return nil, err
	}

	//Filter out only the clients for our env
	for _, val := range blockDeployTo {
		val = strings.ToLower(val) //normalize strings to avoid deploying to intended blocked client
		if strings.HasSuffix(val, "-"+env) {
			val = strings.TrimSuffix(val, "-"+env)
			clients = removeFromSlice(clients, val)
		}
	}
	filteredClients := strings.Join(clients, ",")
	os.WriteFile("filteredDeployClients.txt", []byte(filteredClients+"\n"), 0600)
	fmt.Printf("FILTERED_CLIENTS_LIST=%s\n", filteredClients)
	return clients, nil
}

func getenv(key, defaultValue string) string {
	if value, exist := os.LookupEnv(key); exist {
		return value
	}
	return defaultValue
}

func pathExists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil {
		return true, nil
	}
	if errors.Is(err, os.ErrNotExist) {
		return false, nil
	}
	return false, err
}
func signOfLife(stop chan bool) {
	select {
	case <-stop:
		return
	default:
		for {
			fmt.Println(".")
			time.Sleep(time.Second * 10)
		}
	}

}

func main() {
	RT, err := getReleaseTrainVersion()
	if err != nil {
		log.Fatal(err)
	}

	RT_DIR := "ReleaseTrains/" + RT
	if (RT != "LOCAL_RT_CUT") {
	  // get the year
    	  RT_DIR = "ReleaseTrains/20" + RT[len(RT)-2:] + "/" + RT
	}
	

	// Load YAML config
	k.Load(file.Provider(fmt.Sprintf("%s/services.yaml", RT_DIR)), yaml.Parser())

	// TODO: unmarshal Release Train services into the struct instead of map[string]string
	// out := ReleaseTrain{Version: RT}
	// k.Unmarshal("", &out)
	// fmt.Println(out)

	env := getenv("DEPLOY_TO_ENV", "qai")
	clientsFile := getenv("CLIENTS_FILE", "ALL_CLIENTS.yaml")
	runWithRTDAT := getenv("RUN_WITH_RTDAT", "false")
	oktaToken := getenv("OKTA_TOKEN", "")
	clientsList := getenv("CLIENTS", "")
	//testRunName := getenv("TESTRUN_NAME", "")

	// TODO someday we will stop using Jenkins MultiDeployPipeline and this function could be used
	// var wg sync.WaitGroup
	// startSingleServiceDeployments(&wg, client, env)

	var clients = []string{}
	if (clientsList != "") {
		clientsList = strings.ReplaceAll(clientsList, " ", "")
		clients = strings.Split(clientsList, ",")
	} else {
		clients, err = readSliceFromFile(clientsFile)
		if err != nil {
			log.Fatal(err)
		}
	}

	clients, err = filterBlockedDeploy(fmt.Sprintf("%s/block-deploy-to.yaml", RT_DIR), clients, env)
	if err != nil {
		log.Fatal(err)
	}

	jobs, err := getJobs(len(clients))
	if err != nil {
		fmt.Printf("Failed to get recent job information from jenkins at endpoint: %s/job/multi_deploy_pipeline/api/json\n", JENKINS_URL)
		log.Fatal(err)
	}
	if (strings.ToLower(runWithRTDAT) == "true") { //Run ReleaseTrainDeployAndTest pipeline with main service-versions
		if (oktaToken != "") { oktaToken = "&OKTA_TOKEN=" + oktaToken }
		err = triggerJenkinsReleaseTrainDeployAndTestJob(clients, k, RT, oktaToken)
		if err != nil {
			log.Fatal(err)
		}
	}	else { //Run directly through multi_deploy_pipeline with any overriden client-specific service-versions
		for _, client := range clients {
			client_services_yaml := fmt.Sprintf("%s/%s/services.yaml", RT_DIR, client)
			hasClientVersions, err := pathExists(client_services_yaml)
			if err != nil {
				log.Fatal(err)
			}
			clientK := k.Copy()
			if hasClientVersions { //override specified client versions
				clientK.Load(file.Provider(client_services_yaml), yaml.Parser())
			}
			err = triggerJenkinsMultiPipelineDeployJob(client, env, clientK)
			if err != nil {
				log.Fatal(err)
			}
		}
	}

	responses := make(chan jenkinsRunResponse, len(jobs))
	deployDone := make(chan bool, 1)
	var wg sync.WaitGroup

	for _, job := range jobs {
		wg.Add(1)
		go followDeployJob(job, responses, &wg)

	}
	go signOfLife(deployDone)
	wg.Wait()
	deployDone <- true
	close(responses)
	failedPipelines := make([]string, 0)
	for response := range responses {
		fmt.Printf("resp: %v\n", response)
		if response.Result != "SUCCESS" {
			failedPipelines = append(failedPipelines, response.DisplayName)
		}
		fmt.Printf("%s completed with status: %s\n", response.DisplayName, response.Result)
	}
	if len(failedPipelines) > 0 {
		for _, env := range failedPipelines {
			fmt.Printf("%s deploy failed", env)
		}
		log.Fatalf("%d failed deploy(s)", len(failedPipelines))
	}
}
