Docker Setup
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](/docs/getting-started/00-getting-started.md)

You can use the ODE Docker image to connenct to a Goolge Cloud project and run tests. This is the recommended because it ensures environment consistency regardless of the platform you're using (e.g., Mac, Linux, etc)

#### **Docker**

**Note**: Only headless tests will work from within the Docker context.
```bash
docker run -it --entrypoint bash --rm \
    -v ~/.config/gcloud:/root/.config/gcloud \
    -v ~/.config/gh/config.yml:/root/.config/gh/config.yml \
    -v ~/.config/gh/hosts.yml:/root/.config/gh/hosts.yml \
    gcr.io/takeoff-204116/rq-tools:latest
```

+ You may need to run `gh auth setup-git` to have gh-cli handle git credentials.
+ If you are on Windows or do not have gcloud and gh-cli configured, delete the -v arguments above and log into them from inside the Docker Container.
  + `gcloud auth login` and `gcloud auth application-default login --disable-quota-project`
  + `gh auth login` and `gh auth setup-git`
+ If you are not authenticated to the gcr.io registry, run `gcloud auth configure-docker`


### Build a new Dockerimage locally
Make sure you are in a development environment
```bash
docker build -t <tag> --build-arg GH_PAT=$<GH_TOKEN_VAR> .
```
If you do not have PAT token locally and authenticated with GH via oAuth, run this to pass token to the command above:
```bash
echo $(gh auth token)
```

For more information about running Pytest tests or test scripts, see [Usage](/docs/usage/00-Usage.md).