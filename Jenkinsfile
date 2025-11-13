pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Verificar Python') {
            steps {
                sh '''
                    python3 --version
                    pip3 --version
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