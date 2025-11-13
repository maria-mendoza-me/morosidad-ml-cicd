pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    if ! command -v python3 &> /dev/null; then
                        echo "Python no encontrado, instalando..."
                        apt-get update
                        apt-get install -y python3 python3-pip
                    else
                        echo "Python ya instalado"
                        python3 --version
                    fi
                '''
            }
        }
        
        stage('Instalar Dependencias') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m pytest tests/ -v
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                sh '''
                    python3 src/train.py
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completado exitosamente'
        }
        failure {
            echo 'Pipeline fallo'
        }
        always {
            sh 'ls -la models/ 2>&1 || echo "Carpeta models no creada"'
        }
    }
}