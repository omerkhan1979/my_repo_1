# Shared tokens

This repo is a single source of truth for various tokens shared between the Takeoff applications across the environment.

### How it works
Small presentation is here: [Google Slides](https://docs.google.com/presentation/d/17F4XgsE4FXZnuOUFYfQK_29zIDfDlyZ4YzcZbhnydBM/edit)
Confluence guide: [Confluence](https://takeofftech.atlassian.net/wiki/spaces/SE/pages/2157019349/Shared+tokens+across+env+retailer+k8s+clusters)

Long story short:
1) helm template for creating k8s secrets (using one repo as Single Source of Truth)
2) deployment tool (ArgoCD) to deploy secrets to the clusters
3) Takeoff services consume these secrets  

We are using this scheme for merging values:
`default value + env value + env/retailer value`

### Token types
- **common**
As for now, we have **common** tokens per the whole environment — the value will be the same for every uat for all retailers
Example: `LAUNCHDARKLY_SDK_KEY`

- env/**retailer_specific**
Also, we have tokens which are env/**retailer_specific** specific *(this could be changed easily)*
Example: `SERVICE_WORKER_TOKEN `

### How to add new token

***
**Warning!** All values for secrets should be in encoded in `base64`

You could use this command:
```bash
echo -n "YOUR_SUPER_SECRET_TOKEN" | base64
```
***

Depending which token you want to add (**common** or **retailer_specific**), you should find proper folder to use.

Lets check on example for adding the new environment `lobster-uat`.
```bash
.
├── env
│   └── uat
│       ├── lobster
│       │   └── values.yaml
│       └── values.yaml
```

If you need to add **retailer_specific** token, place it in the `env/uat/lobster/values.yaml` file. Don't forget about `base64` format!

If you want, the new token will exist not only on `lobster-uat` but for every other `retailer-uat` environment, place it in the `env/uat/values.yaml` file. 
