pipeline {
    agent {
        docker {
            image 'python:3.12'
            args '-u root:root'
        }
    }
    
    stages {
        stage('Checkout') {
            steps {
            }
        }
        
        stage('Verificar Python') {
            steps {
                sh '''
                    python --version
                    pip --version
                '''
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    pytest tests/ -v
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completado'
        }
        failure {
            echo 'Pipeline falla'
        }
    }
}