package main

import (
	"fmt"
	"log"
	"sync"
)

// THIS FILE CURRENTLY IS NOT USED
// BUT IT WILL BE LEFT HERE FOR DEMO PURPOSES
// because someday we will stop using Jenkins MultiDeployPipeline
// perhaps will switch to the single service deployment model?

func startSingleServiceDeployments(wg *sync.WaitGroup, client, env string) {
	// loop via keys map to find the service object
	for _, value := range k.KeyMap() {
		// the parent object will have length equal 1
		if len(value) == 1 {
			service := value[0]
			helm_chart_version_key := fmt.Sprintf("%s.helm_chart_version", service)
			helm_chart_version := k.String(helm_chart_version_key)
			image_tag := ""
			if k.String(image_tag) != "" {
				image_tag_key := fmt.Sprintf("%s.image", service)
				image_tag = k.String(image_tag_key)
			}
			wg.Add(1)
			go triggerJenkinsSingleService(wg, service, helm_chart_version, image_tag, client, env)
		}
	}
	wg.Wait()
}

func generateJenkinsDeployJobUrlSingleService(svc, helm_chart_version, image_tag, client, env string) string {
	var jenkinsJobURL string

	if svc == "platform" {
		jenkinsJobURL = fmt.Sprintf("%s/job/Deploy_%s_kubernetes_%s_%s/buildWithParameters?GIT_TAG=%s", JENKINS_URL, svc, client, env, helm_chart_version)
	} else {
		jenkinsJobURL = fmt.Sprintf("%s/job/Deploy_%s_%s_%s/buildWithParameters?GIT_TAG=%s", JENKINS_URL, svc, client, env, helm_chart_version)
	}
	return jenkinsJobURL
}

func triggerJenkinsSingleService(wg *sync.WaitGroup, svc, helm_chart_version, image_tag, client, env string) {
	jenkinsJobURL := generateJenkinsDeployJobUrlSingleService(svc, helm_chart_version, image_tag, client, env)
	err := triggerJenkinsJob(jenkinsJobURL)
	if err != nil {
		log.Fatal(err)
	}
	// debug
	log.Println(svc, helm_chart_version, image_tag, client, env)
	wg.Done()
}
