resource "minikube_cluster" "cluster" {
  driver       = var.driver
  cluster_name = var.cluster_name
  nodes        = 1
  cpus         = var.cpus
  memory       = var.memory
}
