pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'morosidad-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'localhost:5000'  // Ajustar si usas registry real
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements_d.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    pytest tests/ -v --junitxml=test-results.xml
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
                    python src/train.py
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
                    # Detener contenedor anterior si existe
                    docker stop ${IMAGE_NAME}-test || true
                    docker rm ${IMAGE_NAME}-test || true
                    
                    # Iniciar contenedor de prueba
                    docker run -d --name ${IMAGE_NAME}-test \
                        -p 5001:5000 ${IMAGE_NAME}:latest
                    
                    # Esperar que inicie
                    sleep 10
                    
                    # Probar health endpoint
                    curl -f http://localhost:5001/health || exit 1
                    
                    # Detener contenedor de prueba
                    docker stop ${IMAGE_NAME}-test
                    docker rm ${IMAGE_NAME}-test
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    # Detener contenedor en producción si existe
                    docker stop ${IMAGE_NAME}-prod || true
                    docker rm ${IMAGE_NAME}-prod || true
                    
                    # Iniciar nuevo contenedor
                    docker run -d --name ${IMAGE_NAME}-prod \
                        -p 5000:5000 \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest
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