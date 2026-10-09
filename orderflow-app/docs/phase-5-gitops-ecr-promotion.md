# Phase 5 - ECR to GitOps promotion

## Target architecture

```text
Developer
   |
   v
orderflow-app
   |
   v
GitHub Actions
   |-- lint
   |-- test
   |-- SonarQube
   |-- pip-audit
   |-- secret scan
   |-- Docker build
   |-- Trivy
   |
   |  main only
   v
Amazon ECR
   |
   | immutable SHA tag
   v
GitHub App token
   |
   v
orderflow-gitops
   |
   | update Helm image tag
   v
GitOps PR
   |
   v
GitOps validation workflow
   |
   | helm lint / render
   v
Merge to main
   |
   v
Argo CD  <-- Phase 6
   |
   v
K3s/Kubernetes  <-- Phase 6
```

## Why the GitOps repository is separate

The application repository owns source code and CI. The GitOps repository owns Kubernetes desired state. Argo CD is intended to reconcile cluster state from the Git repository containing the desired configuration; Argo CD's documentation explicitly recommends a separate repository for Kubernetes manifests/configuration. See: https://argo-cd.readthedocs.io/en/latest/user-guide/ci_automation/

## Promotion rule

Pull requests and non-main CI runs build and scan the image, but do not publish an image or change the GitOps repository.

A successful `push` to `main`:

1. Builds the production image.
2. Runs all Phase 4 security gates.
3. Pushes the verified image to ECR under `sha-<git-sha>`.
4. Uses a narrowly scoped GitHub App token for `orderflow-gitops`.
5. Updates `helm/orderflow/values-dev.yaml`.
6. Opens a PR in the GitOps repository.

CI does **not** commit directly to GitOps `main`.

## Required GitHub configuration in the application repository

Repository Variables:

```text
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=<12-digit AWS account ID>
GITOPS_APP_CLIENT_ID=<GitHub App client ID>
```

Repository Secrets:

```text
AWS_ACCESS_KEY_ID=<temporary bootstrap credential>
AWS_SECRET_ACCESS_KEY=<temporary bootstrap credential>
GITOPS_APP_PRIVATE_KEY=<GitHub App private key PEM>
SONAR_HOST_URL=<existing SonarQube URL>
SONAR_TOKEN=<existing SonarQube token>
GITLEAKS_LICENSE=<existing Gitleaks license if required>
```

The AWS access-key approach is intentionally temporary for this project stage. The planned AWS/OIDC phase replaces it with GitHub OIDC and an IAM role.

## GitHub App for cross-repository promotion

Create a GitHub App dedicated to CI-to-GitOps automation.

Recommended repository permissions, limited to `orderflow-gitops`:

```text
Contents:       Read and write
Pull requests:  Read and write
Metadata:        Read
```

Install the app only on the GitOps repository. Store its client ID as `GITOPS_APP_CLIENT_ID` and private key as `GITOPS_APP_PRIVATE_KEY`.

GitHub's documentation notes that the normal `GITHUB_TOKEN` is scoped to the repository containing the workflow, so a separate GitHub App installation token is appropriate for cross-repository access. See: https://docs.github.com/en/actions/concepts/security/github_token

## ECR repository

Use one private repository:

```text
orderflow-api
```

Use immutable, commit-derived tags. The CI currently publishes:

```text
sha-<40-character-git-sha>
```

Prefer ECR tag immutability so an existing tag cannot be overwritten. AWS documents immutable tags as the mechanism that prevents a tag from being replaced. See: https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html

## What is intentionally not here yet

```text
Argo CD Application manifest     -> Phase 6
Argo CD installation             -> Phase 6
K3s cluster creation             -> Phase 6
AWS infrastructure Terraform     -> later platform phase
GitHub OIDC / IAM federation     -> later AWS hardening phase
Istio                             -> later service-mesh phase
```

