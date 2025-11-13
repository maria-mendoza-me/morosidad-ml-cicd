pipeline {
    agent any

    environment {
        IMAGE_NAME = 'morosidad-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'localhost:5000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                sh '''
                    echo "=== Verificando Python en el agente ==="
                    PYEXEC=$(command -v python3 || command -v python) || true
                    if [ -z "$PYEXEC" ]; then
                      echo "ERROR: no se encontró python3 ni python en el agente."
                      echo "Instala Python o usa un agent con Python o ejecuta las etapas dentro de un contenedor python."
                      exit 1
                    fi
                    echo "Usando: $PYEXEC -> $($PYEXEC --version 2>/dev/null || true)"
                '''
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    PYEXEC=$(command -v python3 || command -v python) || { echo "No python disponible"; exit 1; }
                    $PYEXEC -m pip install --upgrade pip
                    $PYEXEC -m pip install -r requirements_d.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    PYEXEC=$(command -v python3 || command -v python) || { echo "No python disponible"; exit 1; }
                    $PYEXEC -m pytest tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    PYEXEC=$(command -v python3 || command -v python) || { echo "No python disponible"; exit 1; }
                    $PYEXEC src/train.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                    docker.build("${IMAGE_NAME}:latest")
                }
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                    docker stop ${IMAGE_NAME}-test || true
                    docker rm ${IMAGE_NAME}-test || true
                    docker run -d --name ${IMAGE_NAME}-test -p 5001:5000 ${IMAGE_NAME}:latest
                    sleep 10
                    curl -f http://localhost:5001/health || exit 1
                    docker stop ${IMAGE_NAME}-test
                    docker rm ${IMAGE_NAME}-test
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker stop ${IMAGE_NAME}-prod || true
                    docker rm ${IMAGE_NAME}-prod || true
                    docker run -d --name ${IMAGE_NAME}-prod -p 5000:5000 --restart unless-stopped ${IMAGE_NAME}:latest
                '''
            }
        }
    }

    post {
        success { echo 'Pipeline completado exitosamente!' }
        failure { echo 'Pipeline fallido' }
        always { cleanWs() }
    }
}