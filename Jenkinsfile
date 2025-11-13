pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Verificar Sistema') {
            steps {
                sh '''
                    uname -a || echo "uname no disponible"
                    pwd
                    ls -la
                    python3 --version 2>&1 || python --version 2>&1 || echo "Python NO encontrado"
                    pip3 --version 2>&1 || pip --version 2>&1 || echo "Pip NO encontrado"
                    docker --version 2>&1 || echo "Docker NO encontrado"
                '''
            }
        }
        
        stage('Instalar Dependencias') {
            steps {
                sh '''
                    if command -v python3 &> /dev/null; then
                        python3 -m pip install --upgrade pip
                        pip3 install -r requirements.txt
                    elif command -v python &> /dev/null; then
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                    else
                        echo "Python no esta disponible"
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    if command -v pytest &> /dev/null; then
                        pytest tests/ -v
                    elif command -v python3 &> /dev/null; then
                        python3 -m pytest tests/ -v
                    elif command -v python &> /dev/null; then
                        python -m pytest tests/ -v
                    else
                        echo "Pytest no disponible"
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                sh '''
                    if command -v python3 &> /dev/null; then
                        python3 src/train.py
                    elif command -v python &> /dev/null; then
                        python src/train.py
                    else
                        echo "Python no disponible"
                        exit 1
                    fi
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