# Product Requirements Document (PRD)

## Automated CI/CD Pipeline for a Static To-Do App on Local Kubernetes

| Field | Value |
|-------|-------|
| **Document status** | Draft v1.0 |
| **Date** | 2026-09-16 |
| **Author** | rknishok@gmail.com |
| **Project type** | Infrastructure Automation / DevOps |

---

## 1. Overview

This project delivers a fully automated, infrastructure-as-code (IaC) pipeline that provisions a local Kubernetes cluster, stands up a Jenkins CI server, and continuously builds and deploys a static To-Do web application to that cluster.

The goal is a **single, reproducible, one-command-per-stage workflow** that a developer can run on their own machine to demonstrate an end-to-end DevOps loop: **provision → configure → build → deploy.**

---

## 2. Problem Statement

> Write Terraform scripts to define a local Kubernetes cluster on Minikube. Write an Ansible playbook to install Jenkins inside a Docker container, which then automatically builds and deploys the static To-Do App to Kubernetes.

Manually setting up a cluster, installing CI tooling, and wiring up deployments is slow, error-prone, and non-reproducible. This project automates every step so the environment can be torn down and recreated reliably.

---

## 3. Goals & Non-Goals

### 3.1 Goals
- **G1** — Provision a local Kubernetes cluster on **Minikube** using **Terraform**.
- **G2** — Install and run **Jenkins in a Docker container** using an **Ansible** playbook (no manual clicks).
- **G3** — Configure a Jenkins pipeline that **automatically builds** the static To-Do App into a container image.
- **G4** — **Deploy** the built image to the Minikube cluster via Kubernetes manifests.
- **G5** — Make the running app reachable from the host browser.
- **G6** — Everything reproducible: `destroy` and re-`apply` returns the same state.

### 3.2 Non-Goals
- No cloud (AWS/GCP/Azure) provisioning — local only.
- No production-grade security hardening, TLS, or secrets vaulting (basic only).
- No dynamic backend/database — the To-Do App is **static** (HTML/CSS/JS).
- No multi-node / HA cluster.

---

## 4. Target Users / Personas

| Persona | Need |
|---------|------|
| **DevOps learner / student** | A working, documented reference of a full IaC + CI/CD loop. |
| **Developer** | Push code → see it built and deployed automatically. |
| **Reviewer / Evaluator** | Reproduce the environment from scratch to verify the submission. |

---

## 5. System Architecture

```
Developer machine (host)
│
├── Terraform ──────────► Minikube (local Kubernetes cluster)
│                              ▲
├── Ansible ──► Docker ──► Jenkins container
│                   │
│                   └── Pipeline job:
│                         1. Checkout To-Do App source
│                         2. Build Docker image (static site + nginx)
│                         3. Load/push image to Minikube
│                         4. kubectl apply -f k8s manifests
│                              │
│                              ▼
│                     To-Do App Deployment + Service (NodePort)
│                              │
└──────────── browser ◄───────┘  (minikube service URL)
```

---

## 6. Functional Requirements

### 6.1 Terraform — Cluster Provisioning
- **FR-T1** Define the Minikube cluster as Terraform-managed infrastructure (via the `minikube` provider or a `null_resource`/`local-exec` wrapper calling `minikube start`).
- **FR-T2** Configure cluster parameters: driver (docker), CPUs, memory, Kubernetes version.
- **FR-T3** Output the cluster context / kubeconfig path for downstream tools.
- **FR-T4** Support `terraform apply` (create) and `terraform destroy` (tear down) cleanly.

### 6.2 Ansible — Jenkins Setup
- **FR-A1** Ensure Docker is installed and running on the host.
- **FR-A2** Pull the Jenkins image and run it as a Docker container with persistent volume for `JENKINS_HOME`.
- **FR-A3** Expose Jenkins UI (default port `8080`) and agent port (`50000`).
- **FR-A4** Mount the Docker socket / install `kubectl` + `docker` CLI inside Jenkins so the pipeline can build images and deploy.
- **FR-A5** Retrieve and print the initial admin password (or pre-seed admin via config).
- **FR-A6** (Optional) Pre-install required Jenkins plugins and seed the pipeline job.

### 6.3 Jenkins Pipeline — Build & Deploy
- **FR-J1** Pipeline (declarative `Jenkinsfile`) with stages: **Checkout → Build → Deploy → Verify**.
- **FR-J2** Build a Docker image packaging the static To-Do App behind an nginx server.
- **FR-J3** Make the image available to Minikube (`minikube image load` or a local registry).
- **FR-J4** Apply Kubernetes manifests (`Deployment`, `Service`) to the cluster.
- **FR-J5** Trigger automatically (SCM poll / webhook / on-commit) — not manual only.

### 6.4 Kubernetes — App Deployment
- **FR-K1** `Deployment` running the To-Do App image (configurable replica count, default 1–2).
- **FR-K2** `Service` of type **NodePort** exposing the app.
- **FR-K3** App accessible via `minikube service todo-app --url`.
- **FR-K4** Readiness/liveness probes on the nginx port.

---

## 7. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| **NFR-1** | **Reproducibility** — full teardown + rebuild yields an identical working environment. |
| **NFR-2** | **Idempotency** — re-running Ansible/Terraform causes no harmful side effects. |
| **NFR-3** | **Documentation** — a `README` with prerequisites and exact run order. |
| **NFR-4** | **Portability** — runs on a standard dev machine (Linux/macOS/WSL2/Windows w/ Docker). |
| **NFR-5** | **Speed** — end-to-end provision + first deploy in a reasonable time (target < 15 min). |
| **NFR-6** | **Isolation** — no changes to host beyond declared tools (Docker, Minikube, kubectl). |

---

## 8. Prerequisites / Tooling

| Tool | Purpose |
|------|---------|
| Docker | Container runtime for Minikube + Jenkins |
| Minikube | Local Kubernetes cluster |
| kubectl | Cluster interaction |
| Terraform | Cluster provisioning (IaC) |
| Ansible | Jenkins configuration management |
| Git | Source control for the app + pipeline |

---

## 9. Deliverables

1. `terraform/` — `.tf` files provisioning the Minikube cluster (+ variables, outputs).
2. `ansible/` — playbook + roles to install Docker & run Jenkins.
3. `app/` — static To-Do App source (`index.html`, CSS, JS) + `Dockerfile`.
4. `k8s/` — `deployment.yaml`, `service.yaml`.
5. `Jenkinsfile` — declarative CI/CD pipeline.
6. `README.md` — prerequisites and step-by-step run instructions.
7. This `PRD.md`.

---

## 10. Workflow / Run Order

```bash
# 1. Provision the cluster
cd terraform && terraform init && terraform apply

# 2. Install Jenkins in Docker
cd ../ansible && ansible-playbook jenkins-setup.yml

# 3. In Jenkins UI: unlock, create the pipeline job pointing at the repo
#    (or let the seed job / JCasC configure it automatically)

# 4. Pipeline runs: Checkout → Build image → Load into Minikube → kubectl apply

# 5. Access the app
minikube service todo-app --url
```

---

## 11. Acceptance Criteria

- [ ] `terraform apply` brings up a healthy Minikube cluster (`kubectl get nodes` → Ready).
- [ ] Ansible playbook leaves a running Jenkins container reachable at `localhost:8080`.
- [ ] Jenkins pipeline completes all stages green.
- [ ] `kubectl get pods` shows the To-Do App pod(s) Running.
- [ ] The To-Do App loads in a browser via the NodePort/service URL.
- [ ] A code change → pipeline re-run → redeploys the updated app.
- [ ] `terraform destroy` cleanly removes the cluster.

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Image not visible to Minikube | Use `minikube image load` or point Docker to Minikube's daemon. |
| Jenkins lacks kubectl/docker access | Mount Docker socket + install CLIs in the Ansible role. |
| Terraform Minikube provider quirks | Fall back to `null_resource` + `local-exec` wrapping `minikube` CLI. |
| Port conflicts (8080) | Make ports configurable via variables. |
| Host resource limits | Document minimum CPU/RAM in the README. |

---

## 13. Future Enhancements (Out of Scope for v1)

- Ingress + custom domain instead of NodePort.
- Automated Jenkins config via JCasC + job DSL seed.
- Image scanning / linting stages in the pipeline.
- Monitoring (Prometheus/Grafana) on the cluster.
- Promotion to a real cloud Kubernetes cluster.
