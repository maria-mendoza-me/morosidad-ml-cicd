pipeline {
    agent any

    environment {
        IMAGE_NAME = 'morosidad-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'localhost:5000'  // ajustar si usas otro registry
        WORKDIR = "${WORKSPACE}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Environment') {
            steps {
                sh '''
                    echo "==== Verificando entorno ===="
                    echo "WORKSPACE=$WORKSPACE"
                    echo "User: $(whoami || true)"
                    echo "Python: $(command -v python3 || command -v python || echo none)"
                    echo "Docker cli: $(command -v docker || echo none)"
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    set -e
                    echo "Ejecutando training dentro de un contenedor python (montando WORKSPACE)..."
                    # Ejecuta el training dentro de python:3.11-slim montando el workspace para que los modelos queden en ./models
                    docker run --rm \
                      -u $(id -u):$(id -g) \
                      -v "${WORKSPACE}":/workspace -w /workspace \
                      python:3.11-slim \
                      bash -lc "python -m pip install --no-cache-dir -r requirements_d.txt && python src/train.py"
                    echo "Contenido de models tras train:"
                    ls -la "${WORKSPACE}/models" || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    if ! command -v docker >/dev/null 2>&1; then
                      echo "ERROR: docker no está disponible en este agente. Asegúrate de montar /var/run/docker.sock y tener docker CLI."
                      exit 1
                    fi
                    echo "Construyendo imagen ${IMAGE_NAME}:${IMAGE_TAG} desde ${WORKSPACE}..."
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ${WORKSPACE}
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                    set -e
                    if ! command -v docker >/dev/null 2>&1; then
                      echo "ERROR: docker no está disponible en este agente."
                      exit 1
                    fi
                    echo "Probando contenedor de la imagen..."
                    docker stop ${IMAGE_NAME}-test || true
                    docker rm ${IMAGE_NAME}-test || true
                    docker run -d --name ${IMAGE_NAME}-test -p 5001:5000 ${IMAGE_NAME}:latest
                    sleep 10
                    curl -f http://localhost:5001/health || { echo "Health check falló"; docker logs ${IMAGE_NAME}-test --tail 200 || true; exit 1; }
                    docker stop ${IMAGE_NAME}-test
                    docker rm ${IMAGE_NAME}-test
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    set -e
                    if ! command -v docker >/dev/null 2>&1; then
                      echo "ERROR: docker no está disponible en este agente."
                      exit 1
                    fi
                    echo "Desplegando ${IMAGE_NAME}:latest..."
                    docker stop ${IMAGE_NAME}-prod || true
                    docker rm ${IMAGE_NAME}-prod || true
                    docker run -d --name ${IMAGE_NAME}-prod -p 5000:5000 --restart unless-stopped ${IMAGE_NAME}:latest
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completado exitosamente!'
        }
        failure {
            echo 'Pipeline fallido'
        }
        always {
            cleanWs()
        }
    }
}