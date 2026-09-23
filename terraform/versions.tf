terraform {
  required_providers {
    minikube = {
      source = "scott-the-programmer/minikube"
      version = "0.4.4"
    }
  }
  required_version = ">= 1.5.0"
}

provider "minikube" {
  kubernetes_version = var.kubernetes_version
}
