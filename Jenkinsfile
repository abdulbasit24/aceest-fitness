pipeline {
    agent any

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
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '── Running flake8 linter ──'
                sh '''
                    . venv/bin/activate
                    flake8 app.py test_app.py --max-line-length=100
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo '── Running Pytest suite ──'
                sh '''
                    . venv/bin/activate
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
                echo '── Removing venv ──'
                sh 'rm -rf venv'
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