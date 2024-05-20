Project Structure and definition
==
[[Table of Contents](../../README.md#table-of-contents)] : [Project Structure](./00-project_structure.md)

## Project Structure

```bash
.
├── ALL_CLIENTS.yaml
├── Makefile
├── README.md
├── RT_SERVICES.yaml
├── ReleaseTrains
│   ├── 2021
│   │   ├── RT40-21
│   │   │   ├── block-deploy-to.yaml
│   │   │   ├── clients-deployed-to-prod.yaml
│   │   └── services.yaml
│   │   ├── RT42-21
│   │   │   ├── block-deploy-to.yaml
│   │   │   ├── clients-deployed-to-prod.yaml
│   │   │   ├── services.yaml
│   │   │   ├── pinemelon
│   │   │   │   └── services.yaml
│   │   │   └── tangerine
│   │   │   │   └── services.yaml
│   ├── ...
├── ReleaseTrains.yaml
├── go.mod
├── go.sum
└── rt-deploy-tool
    ├── app
    │   ├── main.go
    │   ├── multi_deploy_jenkins.go
    │   ├── rt_version.go
    │   └── single_svc.go
    └── ops
        └── Dockerfile

```

### Project Structure Definition

* `ALL_CLIENTS.yaml`
   - List of the clients we currently deploy to
   - Note: If we were to do a rollback type of thing, we would need to track this at the RT Folder level
* `Makefile`
   - Used to build/run from CMDLine
* `README.md`
   - This file
* `RT_SERVICES.yaml`
   - List of services included on Release Trains
* `ReleaseTrains`
   - `2021` YEAR OF TRAINS 
      - `RT42-21`
         - `services.yaml`
            - Identifies all services/versions on the RT
         - `block-deploy-to.yaml`
            - This file can be used to block for any-and-all client-levels: `tangerine-qai`, `tangerine-uat`, `tangerine-prod`
            - We should create the git RT folder and the `block-deploy-to.yaml` file only in the AM and allow people to add to the `block-deploy-to.yaml` if needed
         - `clients-deployed-to-prod.yaml`
            - Could be used to determine if we should include an update/hotfix updated (by PR) in main services.yaml (see #2 in [this comment](https://takeofftech.atlassian.net/browse/PROD-1083?focusedCommentId=131361))
            - Could also be used to handle rollbacks (see ReleaseTrains.yaml above)
      - `tangerine`
         - `services.yaml`
            - contains service/version details specific for tangerine (treat as an override for parent services.yaml)
      - `{other-client-name}`
         - `services.yaml`
            - override for <other-client> service/versions   
* `ReleaseTrains.yaml`
   - Lists the Release Trains in the Repo.
   - Currently, the `datetime` shown below is generated with this command `date +%Y-%m-%d@%H%M`
   - The date format can be changed to anything we like... I only used it for example
   - This file is auto-updated at RT-Cut time to append a new line akin to below:
      - RT40-21: 2021-10-06@1201
      - RT42-21: 2021-10-20@1201
      - RT{xx}={datetime of RT-Cut}
   - In the future, this file could also allow us to roll-back/re-deploy-earlier-version if we need to, by pulling from ReleaseTrains.yaml with something like `tail -2 ReleaseTrains.yaml | head -1`
      - To consider: what to do with clients that skip trains
      - See clients-deployed-to-prod.yaml below
      - Maintain a SkippedProdDeploy folder or file with details of client tangerine.yaml so we can roll back correctly
* `go.mod` and `go.sum`
   - Golang module files
* `rt-deploy-tool`
   - `app`
      - `main.go`
         - The 'main' Golang file for the `deploy` program 
      - ` multi_deploy_jenkins.go`
         - Golang helper methods
      - `rt_version.go`
         - Golang helper methods
      - `single_svc.go`
         - Not currently in use... Future Thinking
   - `ops`
      - `Dockerfile`
         - Not currently in use (may be removed in future)
