# gitops-dr-demo-app

GitOps Disaster Recovery Demo App — a simple but realistic demo application designed as a foundation for later GitOps-based disaster recovery workflows.

## Repository Layout

```
gitops-dr-demo-app/
├── app/
│   ├── backend/
│   └── frontend/
├── k8s/
│   ├── base/
│   └── overlays/
│       ├── dev/
│       └── dr/
├── gitops/
├── .gitignore
└── README.md
```

## Contents

- **app/backend**: Python Flask API exposing `/api/status`.
- **app/frontend**: Static HTML UI served by Nginx, proxies `/api/` to the backend.
- **k8s/base**: Namespace, deployments, and services (ClusterIP for backend, NodePort for frontend).
- **k8s/overlays/dev**: Kustomize overlay referencing base (dev defaults).
- **k8s/overlays/dr**: Kustomize overlay that patches frontend and backend to 2 replicas (DR).
- **gitops/argocd-application.yaml**: Argo CD Application pointing at the `dev` overlay with automated sync (self-heal + prune).

## Build Instructions

### 1. Build backend image

Replace the image name/tag with your registry if needed.

```bash
docker build -t ghcr.io/SarraMehrez/gitops-dr-demo-backend:latest -f app/backend/Dockerfile app/backend
```

### 2. Build frontend image

```bash
docker build -t ghcr.io/SarraMehrez/gitops-dr-demo-frontend:latest -f app/frontend/Dockerfile app/frontend
```

### 3. Push images to your registry (example using GitHub Container Registry)

```bash
docker push ghcr.io/SarraMehrez/gitops-dr-demo-backend:latest
docker push ghcr.io/SarraMehrez/gitops-dr-demo-frontend:latest
```

## Kubernetes (kustomize) — Local Install

### Apply the dev overlay

Creates namespace and resources:

```bash
kubectl apply -k k8s/overlays/dev
```

### Verify resources

```bash
kubectl get all -n gitops-demo
```

### Access the frontend (NodePort)

- If running on a local cluster (Minikube), get node IP and use nodePort 30080:
  ```bash
  minikube ip
  # then visit http://<MINIKUBE_IP>:30080
  ```
- On other clusters, access any node on port 30080.

## Switch to DR Overlay

To apply the DR overlay (which patches both backend and frontend replicas from 1 → 2):

```bash
kubectl apply -k k8s/overlays/dr
```

To revert to dev overlay:

```bash
kubectl apply -k k8s/overlays/dev
```

## Argo CD Usage

### 1. Install Argo CD

Install Argo CD in your cluster (if not installed). Quickstart:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Create the Argo CD Application

```bash
kubectl apply -f gitops/argocd-application.yaml
```

This Application points to `k8s/overlays/dev` in this repository and uses automated sync with `prune` and `selfHeal` enabled. Argo CD will deploy the `dev` overlay into the `gitops-demo` namespace.

### 3. Access the Argo CD UI

Port-forward example:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
# Open https://localhost:8080
```

## Notes

- The Kubernetes manifests use the images:
  - `ghcr.io/SarraMehrez/gitops-dr-demo-backend:latest`
  - `ghcr.io/SarraMehrez/gitops-dr-demo-frontend:latest`

  Update these image references as needed for your registry / CI pipeline.

- The DR overlay only changes replica counts (1 → 2) for both backend and frontend. No DR tooling (Velero, Stash, etc.) is included — this repo prepares the foundation for GitOps-driven DR automation.

- The frontend proxies `/api/` to a Kubernetes service named `backend` on port 5000. Ensure DNS/service names match when deploying into other namespaces or environments.

## Troubleshooting

- If pods cannot pull images, either push images to the referenced registry or modify the `image:` fields in `k8s/base/*` to point to images available to your cluster.
- To inspect Argo CD application sync status:
  ```bash
  kubectl -n argocd get applications
  kubectl -n argocd describe application gitops-dr-demo-app-dev
  ```

## License

MIT