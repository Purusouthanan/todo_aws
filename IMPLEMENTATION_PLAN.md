# Implementation Plan

## Automated CI/CD Pipeline for a Static To-Do App on Local Kubernetes

**Companion to:** [PRD.md](PRD.md)
**Date:** 2026-09-16
**Status:** Draft v1.0

---

## 0. High-Level Strategy

Build in **four layers**, bottom-up, verifying each layer works before moving on. This avoids debugging a broken end-to-end pipeline where you can't tell which layer failed.

```
Layer 4:  Jenkins pipeline (build + deploy)      ← ties it all together
Layer 3:  Kubernetes manifests + app + Dockerfile ← the thing being deployed
Layer 2:  Ansible → Jenkins in Docker            ← the CI engine
Layer 1:  Terraform → Minikube cluster           ← the foundation
```

**Build order:** Layer 1 → 3 → 2 → 4
(We build the app/manifests in Layer 3 before Jenkins in Layer 2, so that when Jenkins comes online there is already something concrete for its pipeline to build and deploy.)

---

## 1. Prerequisites Check (Phase 0)

Before writing anything, confirm the host has:

| Tool | Verify command | Expected |
|------|---------------|----------|
| Docker | `docker version` | Client + Server running |
| Minikube | `minikube version` | v1.3x+ |
| kubectl | `kubectl version --client` | v1.2x+ |
| Terraform | `terraform version` | v1.5+ |
| Ansible | `ansible --version` | v2.14+ |

> On Windows: run Ansible from **WSL2** (Ansible does not run natively on Windows). Docker Desktop with WSL2 backend is recommended. Terraform, Minikube, and kubectl can run in either Windows or WSL2 — keep them consistent (recommend all in WSL2).

**Deliverable:** a `docs/prerequisites.md` note capturing versions used.

---

## 2. Proposed Repository Structure

```
to-do/
├── PRD.md
├── IMPLEMENTATION_PLAN.md
├── README.md
│
├── app/                        # Layer 3 — the static To-Do App
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── Dockerfile
│   └── nginx.conf              # (optional custom config)
│
├── k8s/                        # Layer 3 — Kubernetes manifests
│   ├── deployment.yaml
│   └── service.yaml
│
├── terraform/                  # Layer 1 — cluster provisioning
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf
│
├── ansible/                    # Layer 2 — Jenkins setup
│   ├── jenkins-setup.yml
│   ├── inventory.ini
│   ├── ansible.cfg
│   └── roles/
│       ├── docker/             # ensure Docker present
│       │   └── tasks/main.yml
│       └── jenkins/            # run Jenkins container + tooling
│           ├── tasks/main.yml
│           ├── templates/
│           │   └── Dockerfile.jenkins.j2   # custom Jenkins image w/ kubectl+docker
│           └── vars/main.yml
│
└── Jenkinsfile                 # Layer 4 — the pipeline
```

---

## 3. Phase 1 — Terraform: Minikube Cluster

### 3.1 Approach decision
Two options for provisioning Minikube with Terraform:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A. `scott-the-programmer/minikube` provider** | Native, declarative, clean state | Provider can lag Minikube versions | **Primary** |
| **B. `null_resource` + `local-exec` → `minikube start`** | Always works, simple | Not truly declarative, weaker state | **Fallback** |

Start with **Option A**; if the provider misbehaves, drop to **Option B**.

### 3.2 Files to write
- **`versions.tf`** — pin Terraform + provider versions.
- **`variables.tf`** — `cluster_name`, `driver` (default `docker`), `cpus`, `memory`, `kubernetes_version`.
- **`main.tf`** — the `minikube_cluster` resource (Option A) *or* `null_resource` (Option B).
- **`outputs.tf`** — kubeconfig context name, client cert/key paths, cluster host.

### 3.3 Verification
```bash
cd terraform
terraform init
terraform apply -auto-approve
kubectl get nodes        # → node "minikube" Ready
minikube status          # → host/kubelet/apiserver Running
```

**Exit criteria:** `kubectl get nodes` returns a Ready node.

---

## 4. Phase 2 — The App, Dockerfile & K8s Manifests (Layer 3)

### 4.1 Static To-Do App (`app/`)
- **`index.html`** — To-Do UI (input box, add button, list).
- **`style.css`** — basic styling.
- **`app.js`** — add/complete/delete todos; persist to `localStorage` (no backend needed for a static app).

> Keep it genuinely static — all logic client-side. This satisfies the "static To-Do App" requirement and keeps deployment simple (just nginx serving files).

### 4.2 Dockerfile (`app/Dockerfile`)
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
# optional: COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 4.3 Kubernetes manifests (`k8s/`)
- **`deployment.yaml`**
  - image: `todo-app:latest`
  - `imagePullPolicy: IfNotPresent` (critical — so it uses the locally-loaded image, not Docker Hub)
  - replicas: 2
  - readiness + liveness probes on port 80
- **`service.yaml`**
  - type: `NodePort`
  - port 80 → nodePort (e.g. 30080)

### 4.4 Manual verification (before Jenkins exists)
```bash
# build image directly into minikube's docker daemon
eval $(minikube docker-env)      # (Linux/mac/WSL)
docker build -t todo-app:latest ./app
kubectl apply -f k8s/
kubectl get pods                 # → Running
minikube service todo-app --url  # → open URL in browser
```

**Exit criteria:** the To-Do App loads in a browser. This proves the app + manifests are correct *independently* of Jenkins, so any later failure is isolated to the CI layer.

---

## 5. Phase 3 — Ansible: Jenkins in Docker (Layer 2)

### 5.1 What Jenkins needs
The Jenkins container must be able to **build Docker images** and **run kubectl** against Minikube. So we build a **custom Jenkins image** that bundles:
- Docker CLI (talks to host Docker via mounted socket)
- kubectl
- A mounted kubeconfig + Minikube certs so kubectl can reach the cluster

### 5.2 `roles/docker`
- Ensure Docker installed & running (idempotent; skip install if present).

### 5.3 `roles/jenkins`
- **`templates/Dockerfile.jenkins.j2`** — `FROM jenkins/jenkins:lts-jdk17`, install docker-ce-cli + kubectl.
- **`tasks/main.yml`**:
  1. Build the custom Jenkins image.
  2. Run container:
     - name `jenkins`
     - ports `8080:8080`, `50000:50000`
     - volumes:
       - `jenkins_home` (named volume — persistence)
       - `/var/run/docker.sock:/var/run/docker.sock` (build images)
       - host `~/.kube` and `~/.minikube` mounted read-only (kubectl access)
     - restart policy `unless-stopped`
  3. Wait for Jenkins to be up (poll `:8080/login`).
  4. Read + display the initial admin password from the container.

### 5.4 Key config decisions
| Decision | Choice | Why |
|----------|--------|-----|
| Jenkins persistence | Named Docker volume | Survives container restarts |
| Docker access | Mount host socket | Simplest; avoids Docker-in-Docker complexity |
| kubectl access | Mount `~/.kube` + `~/.minikube` | Jenkins reuses host's cluster credentials |
| Networking to Minikube | `--network host` *or* fix kubeconfig server IP | Container must reach the API server |

> **Watch-out:** the kubeconfig points at `https://127.0.0.1:<port>` or a Minikube IP. Inside the Jenkins container `127.0.0.1` is the container itself. Mitigation: run Jenkins with `--network host`, **or** rewrite the server address to the Minikube IP (`minikube ip`) in a mounted kubeconfig.

### 5.5 Verification
```bash
cd ansible
ansible-playbook jenkins-setup.yml
# → open http://localhost:8080, unlock with printed password
# inside container sanity check:
docker exec jenkins kubectl get nodes   # → Ready (proves cluster access)
docker exec jenkins docker ps           # → proves docker access
```

**Exit criteria:** Jenkins UI reachable AND `kubectl get nodes` works from inside the container.

---

## 6. Phase 4 — Jenkins Pipeline (Layer 4)

### 6.1 `Jenkinsfile` (declarative)
Stages:

| Stage | Action |
|-------|--------|
| **Checkout** | Pull the repo (app + k8s manifests + Jenkinsfile). |
| **Build** | `docker build -t todo-app:<BUILD_NUMBER> -t todo-app:latest ./app` |
| **Load to Minikube** | `minikube image load` *or* build against Minikube's docker daemon so the cluster can pull it. |
| **Deploy** | `kubectl apply -f k8s/` then `kubectl set image` / `kubectl rollout restart` to pick up the new build. |
| **Verify** | `kubectl rollout status deployment/todo-app` and a `curl` smoke test against the service. |

### 6.2 Making the image available to Minikube (important)
Since we use the host Docker socket, build the image on the host Docker, then:
- `minikube image load todo-app:latest`, **or**
- configure the build to target Minikube's docker-env.
Manifest already uses `imagePullPolicy: IfNotPresent` so it won't try Docker Hub.

### 6.3 Job setup in Jenkins
- Create a **Pipeline** job → "Pipeline script from SCM" → point at the Git repo → `Jenkinsfile`.
- Trigger: **SCM polling** (`H/2 * * * *`) or a webhook for auto-build on commit (FR-J5).
- (Stretch) Automate this job creation via **Job DSL / JCasC** so no manual UI clicks are needed.

### 6.4 Verification
```bash
# Trigger a build (commit a change or click Build Now)
# Watch console: Checkout → Build → Load → Deploy → Verify all green
kubectl get pods                 # new pods rolled out
minikube service todo-app --url  # updated app served
```

**Exit criteria:** a commit/trigger produces a green pipeline and the updated app is live.

---

## 7. Phase 5 — Documentation & End-to-End Test

1. Write **`README.md`** — prerequisites, exact run order, troubleshooting, teardown.
2. Full clean run test:
   ```bash
   terraform apply           # cluster up
   ansible-playbook ...      # Jenkins up
   # configure/trigger pipeline → app deployed
   # change a todo label in index.html, commit → pipeline redeploys
   terraform destroy         # clean teardown
   ```
3. Confirm every **Acceptance Criterion** in the PRD (§11) passes; tick the checkboxes.

---

## 8. Task Breakdown & Sequencing

| # | Task | Layer | Depends on | Est. |
|---|------|-------|-----------|------|
| 1 | Prereq check + versions doc | 0 | — | 0.5h |
| 2 | Terraform cluster (main/vars/outputs) | 1 | 1 | 2h |
| 3 | Verify cluster Ready | 1 | 2 | 0.25h |
| 4 | Static To-Do App (html/css/js) | 3 | — | 2h |
| 5 | Dockerfile + local image build | 3 | 4 | 0.5h |
| 6 | K8s deployment + service | 3 | 5 | 1h |
| 7 | Manual deploy to Minikube (verify app) | 3 | 3,6 | 0.5h |
| 8 | Ansible docker role | 2 | 1 | 0.5h |
| 9 | Custom Jenkins Dockerfile (kubectl+docker) | 2 | 8 | 1h |
| 10 | Ansible jenkins role (run container) | 2 | 9 | 1.5h |
| 11 | Verify Jenkins UI + cluster access | 2 | 10 | 0.5h |
| 12 | Jenkinsfile (all stages) | 4 | 7,11 | 2h |
| 13 | Create/seed pipeline job + trigger | 4 | 12 | 1h |
| 14 | End-to-end run + fix issues | all | 13 | 2h |
| 15 | README + docs + acceptance sign-off | 5 | 14 | 1h |

**Rough total:** ~18–19 hours of focused work.

---

## 9. Key Risks & Mitigations (implementation-specific)

| Risk | Where | Mitigation |
|------|-------|-----------|
| Minikube provider version drift | Phase 1 | Fall back to `null_resource` + `local-exec`. |
| kubeconfig `127.0.0.1` unreachable from container | Phase 3 | `--network host` or rewrite server to `minikube ip`. |
| Image not found in cluster (pulls Docker Hub) | Phase 4 | `imagePullPolicy: IfNotPresent` + `minikube image load`. |
| Docker socket permission denied in Jenkins | Phase 3 | Add jenkins user to docker group / adjust socket perms. |
| Windows-native Ansible fails | Phase 0 | Run Ansible from WSL2. |
| Port 8080 already in use | Phase 3 | Make Jenkins host port a variable. |
| New build not picked up (same `latest` tag) | Phase 4 | Tag with `$BUILD_NUMBER` + `kubectl rollout restart`. |

---

## 10. Definition of Done

- [ ] `terraform apply` → healthy Minikube cluster.
- [ ] `ansible-playbook` → Jenkins running in Docker, reachable, with cluster + docker access.
- [ ] Pipeline builds the image and deploys to the cluster automatically.
- [ ] App reachable in browser via NodePort.
- [ ] Code change → auto rebuild + redeploy verified.
- [ ] `terraform destroy` → clean teardown.
- [ ] README lets a fresh user reproduce everything.

---

## 11. Suggested Next Step

Start with **Phase 1 (Terraform)** and **Phase 2 (app + manifests)** in parallel since they're independent — then converge on Jenkins. Say the word and I'll scaffold the actual files.
