pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        IMAGE_NAME = "aceest-fitness"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '── Pulling latest code from GitHub ──'
                checkout scm
            }
        }

        stage('Build Environment') {
            steps {
                echo '── Installing Python dependencies ──'
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8 pytest pytest-cov
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '── Running flake8 linter ──'
                sh '''
                    flake8 app.py test_app.py --max-line-length=100
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo '── Running Pytest suite ──'
                sh '''
                    pytest test_app.py -v --junitxml=results.xml --cov=app --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo '── Building Docker image ──'
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Docker Test') {
            steps {
                echo '── Running tests inside container ──'
                sh """
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                        python -m pytest test_app.py -v
                """
            }
        }

        stage('Cleanup') {
            steps {
                echo '── Cleanup complete ──'
            }
        }
    }

    post {
        success {
            echo "✅ BUILD #${env.BUILD_NUMBER} PASSED – Image: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "❌ BUILD #${env.BUILD_NUMBER} FAILED – Check logs above."
        }
    }
}