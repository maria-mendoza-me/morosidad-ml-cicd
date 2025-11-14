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
                        echo "Instala Python en el contenedor Jenkins o usa un agente que lo tenga."
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
                sh '''
                    if ! command -v docker >/dev/null 2>&1; then
                      echo "ERROR: docker no está disponible en este agente. Para construir la imagen, instala docker o ejecuta este stage en un nodo con Docker."
                      exit 1
                    fi
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                    if ! command -v docker >/dev/null 2>&1; then
                      echo "ERROR: docker no está disponible en este agente. No se puede ejecutar contenedores."
                      exit 1
                    fi
                    docker stop ${IMAGE_NAME}-test || true
                    docker rm ${IMAGE_NAME}-test || true
                    docker run -d --name ${IMAGE_NAME}-test -p 5001:5000 ${IMAGE_NAME}:latest
                    sleep 10
                    curl -f http://localhost:5001/health || { echo "Health check falló"; exit 1; }
                    docker stop ${IMAGE_NAME}-test
                    docker rm ${IMAGE_NAME}-test
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    if ! command -v docker >/dev/null 2>&1; then
                      echo "ERROR: docker no está disponible en este agente. No se puede desplegar."
                      exit 1
                    fi
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