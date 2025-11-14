pipeline {
  agent any

  environment {
    IMAGE_NAME = "morosidad-api"
    IMAGE_TAG  = "${BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Verify') {
      steps {
        echo "WORKSPACE = ${env.WORKSPACE}"
        sh 'echo "Docker support (docker pipeline): $(groovy.lang.GroovySystem.getProperty(\"os.name\") ?: \"unknown\")" || true'
      }
    }

    stage('Train Model') {
      steps {
        script {
          // Ejecutar training dentro de un contenedor python; el plugin Docker Pipeline monta el workspace en el contenedor.
          // Se crea el venv/instala dependencias y se ejecuta src/train.py dentro del contenedor.
          docker.image('python:3.11-slim').inside("-u 1000:1000") {
            sh '''
              set -e
              python -m pip install --upgrade pip
              pip install --no-cache-dir -r requirements_d.txt
              python src/train.py
              echo "Listado models en workspace:"
              ls -la models || true
            '''
          }
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          // Usar docker.build (funcionalidad del plugin Docker Pipeline)
          echo "Construyendo imagen ${IMAGE_NAME}:${IMAGE_TAG} ..."
          def img = docker.build("${IMAGE_NAME}:${IMAGE_TAG}", "${WORKSPACE}")
          // tag latest local
          img.tag("${IMAGE_NAME}:latest", true)
        }
      }
    }

    stage('Test Container') {
      steps {
        script {
          // Levantar la imagen en un container temporal y hacer healthcheck.
          // withRun publica los puertos del contenedor al host.
          echo "Probando contenedor ${IMAGE_NAME}:latest ..."
          docker.image("${IMAGE_NAME}:latest").withRun('-p 5001:5000 --name ${IMAGE_NAME}-test') { c ->
            // Esperar un poco para inicio y probar health endpoint desde el agente (HOST)
            sh '''
              set -e
              echo "Esperando 8s para que el contenedor arranque..."
              sleep 8
              echo "Comprobando /health en http://localhost:5001 ..."
              curl -f http://localhost:5001/health
            '''
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        script {
          echo "Desplegando ${IMAGE_NAME}:latest en un contenedor productivo (detener si existe)..."
          // Intentar detener/eliminar contenedor previo si existe (usa docker pipeline .run para crear el nuevo)
          // Primero intentar parar/elimnar con docker CLI por si existe. Si no hay CLI, el plugin maneja run.
          try {
            // Detener y eliminar (si existe) usando docker CLI si está disponible en el agente:
            sh 'docker stop ${IMAGE_NAME}-prod || true'
            sh 'docker rm ${IMAGE_NAME}-prod || true'
          } catch (err) {
            echo "No se pudo ejecutar docker stop/rm vía shell (puede no existir docker CLI). Continúo con docker Pipeline."
          }
          // Ejecutar contenedor en background usando la API del plugin
          def prod = docker.image("${IMAGE_NAME}:latest").run("-d -p 5000:5000 --name ${IMAGE_NAME}-prod --restart unless-stopped")
          // opcional: mostrar id
          echo "Contenedor productivo lanzado (id): ${prod.id}"
        }
      }
    }
  }

  post {
    success {
      echo "Pipeline completado correctamente"
    }
    failure {
      echo "Pipeline falló"
    }
    always {
      cleanWs()
    }
  }
}