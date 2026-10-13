// Part C - CI/CD pipeline
// Triggered automatically on every commit on the main branch, then:
//   1. builds the app + runs the unit tests
//   2. builds the Docker image and pushes it to Docker Hub
pipeline {
    agent any

    environment {
        // CHANGE THIS to your own Docker Hub username
        DOCKERHUB_USER = 'your-dockerhub-username'
        IMAGE          = "${DOCKERHUB_USER}/counter-app"
        TAG            = "${env.BUILD_NUMBER}"
    }

    triggers {
        // Option 1 (works locally, no public URL): check Git every 2 minutes.
        pollSCM('H/2 * * * *')
        // Option 2 (instant): GitHub webhook -> needs the "GitHub" plugin and a
        // public Jenkins URL (e.g. via ngrok). Uncomment to use it:
        // githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Unit tests') {
            steps {
                dir('app') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install -q -r requirements.txt
                        python -m unittest discover -v -s tests -t .
                    '''
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
            }
        }

        stage('Push to Docker Hub') {
            when { branch 'main' }   // only publish from the main branch
            steps {
                // "dockerhub-creds" = Jenkins credential (Username + Access Token)
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                        echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
                        docker push $IMAGE:$TAG
                        docker push $IMAGE:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        success {
            echo "Image published: ${IMAGE}:${TAG}"
        }
        failure {
            echo 'Pipeline failed - check the stage logs above.'
        }
    }
}
