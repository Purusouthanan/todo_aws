variable "cluster_name" {
  description = "Name of the Minikube cluster"
  type        = string
  default     = "minikube"
}

variable "driver" {
  description = "Driver to use for Minikube"
  type        = string
  default     = "docker"
}

variable "cpus" {
  description = "Amount of CPUs to allocate to Minikube"
  type        = number
  default     = 2
}

variable "memory" {
  description = "Amount of RAM to allocate to Minikube (in MB)"
  type        = string
  default     = "4096"
}

variable "kubernetes_version" {
  description = "Version of Kubernetes to run"
  type        = string
  default     = "v1.30.0"
}
