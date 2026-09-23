pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                // For a real pipeline, this connects to Git.
                // For local demo, the pipeline job is configured with the local path.
            }
        }
        stage('Build Image') {
            steps {
                echo 'Building Docker Image...'
                dir('app') {
                    // Uses the host's Docker socket mounted in the Jenkins container
                    sh 'docker build -t todo-app:latest .'
                }
            }
        }
        stage('Deploy to K8s') {
            steps {
                echo 'Deploying to Kubernetes...'
                // Using docker to run kubectl so we don't have to install it inside Jenkins
                dir('k8s') {
                    sh 'docker run --rm --net host -v ~/.kube:/root/.kube -v ~/.minikube:/root/.minikube -v $(pwd):/k8s bitnami/kubectl:latest apply -f /k8s/'
                }
            }
        }
    }
}
