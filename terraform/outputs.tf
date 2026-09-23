output "cluster_name" {
  description = "The name of the created Minikube cluster"
  value       = minikube_cluster.cluster.cluster_name
}

output "host" {
  description = "The host of the cluster"
  value       = minikube_cluster.cluster.host
}
