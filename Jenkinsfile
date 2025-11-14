pipeline {
  agent any

  environment {
    IMAGE_NAME = "morosidad-api"
    IMAGE_TAG  = "${BUILD_NUMBER}"
    // variable que se define en runtime en la etapa Verify
    DOCKER_AVAILABLE = "unknown"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Verify') {
      steps {
        script {
          echo "==== Verify: comprobando disponibilidad de Docker (de forma segura) ===="
          // Intentamos ejecutar un contenedor muy ligero con el Docker Pipeline plugin.
          // Si falla, no abortamos aquí: marcamos DOCKER_AVAILABLE=false y continuamos con fallback.
          def ok = false
          try {
            // Este bloque lanzará un contenedor si el daemon y el plugin están disponibles.
            docker.image('alpine:3.18').inside {
              sh 'echo "Docker inside test OK"'
            }
            ok = true
          } catch (err) {
            echo "No fue posible ejecutar contenedor con Docker Pipeline: ${err}"
            ok = false
          }

          if (ok) {
            env.DOCKER_AVAILABLE = "true"
            echo "Docker parece disponible. Continuaremos usando Docker Pipeline para build/test/deploy."
          } else {
            env.DOCKER_AVAILABLE = "false"
            echo "ADVERTENCIA: Docker NO disponible desde este agente. El pipeline intentará fallback para training y saltará el build de imagen."
            echo "Si esperas que Jenkins haga docker.build, asegúrate de que el daemon Docker sea accesible desde Jenkins (ej. /var/run/docker.sock montado en el contenedor Jenkins o agente con Docker)."
          }

          // Información adicional para debugging (no es determinante)
          echo "WORKSPACE = ${env.WORKSPACE}"
          echo "NODE_NAME = ${env.NODE_NAME}"
        }
      }
    }

    stage('Train Model') {
      steps {
        script {
          echo "==== Train Model: DOCKER_AVAILABLE=${env.DOCKER_AVAILABLE} ===="
          // Si Docker está disponible, ejecutar training dentro de un contenedor python (plugin Docker Pipeline monta el workspace).
          if (env.DOCKER_AVAILABLE == "true") {
            docker.image('python:3.11-slim').inside("-u 1000:1000") {
              sh '''
                set -e
                python -m pip install --upgrade pip
                pip install --no-cache-dir -r requirements_d.txt
                python src/train.py
                echo "Listado de models (dentro del contenedor):"
                ls -la models || true
              '''
            }
          } else {
            // Fallback: intentar ejecutar training en el propio agente (sin Docker).
            echo "Docker no disponible: intentando ejecutar training en el agente directamente (fallback)."
            def rc = sh(script: '''
              set -e
              python -m pip install --upgrade pip || true
              pip install --no-cache-dir -r requirements_d.txt || true
              python src/train.py
            ''', returnStatus: true)
            if (rc != 0) {
              error("El training falló en el agente y Docker no está disponible. Revisa que el agente tenga Python y dependencias o habilita Docker para Jenkins.")
            }
          }

          // Aseguramos que los modelos queden guardados en el workspace del job
          echo "Contenido final de models en WORKSPACE:"
          sh 'ls -la ${WORKSPACE}/models || true'

          // Stash para que si Build corre en otro agente/worker, los modelos se puedan transferir
          stash includes: 'models/**', name: 'models-stash', allowEmpty: true
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          echo "==== Build Docker Image: DOCKER_AVAILABLE=${env.DOCKER_AVAILABLE} ===="
          // Si Docker no está disponible, salteamos el build pero dejamos mensaje claro.
          if (env.DOCKER_AVAILABLE != "true") {
            echo "Saltando docker.build porque Docker no está disponible en este agente."
            // Opcional: fallar en lugar de saltar:
            // error("Docker no disponible: no puedo construir la imagen.")
          } else {
            // Garantizar que los modelos están presentes (unstash si fue necesario)
            unstash 'models-stash' // si no hay nada no falla por allowEmpty en stash
            sh 'ls -la models || true'

            echo "Construyendo imagen ${IMAGE_NAME}:${IMAGE_TAG} ..."
            def img = docker.build("${IMAGE_NAME}:${IMAGE_TAG}", "${WORKSPACE}")
            // Etiquetar latest localmente
            img.tag("${IMAGE_NAME}:latest", true)
            echo "Imagen construida: ${IMAGE_NAME}:${IMAGE_TAG}"
          }
        }
      }
    }

    stage('Test Container') {
      steps {
        script {
          echo "==== Test Container: DOCKER_AVAILABLE=${env.DOCKER_AVAILABLE} ===="
          if (env.DOCKER_AVAILABLE != "true") {
            echo "Docker no disponible: saltando pruebas de contenedor."
          } else {
            // Levantar y probar la imagen construida
            docker.image("${IMAGE_NAME}:latest").withRun('-p 5001:5000 --name ${IMAGE_NAME}-test') { c ->
              sh '''
                set -e
                echo "Esperando 8s para que el contenedor arranque..."
                sleep 8
                echo "Comprobando /health en http://localhost:5001 ..."
                curl -f http://localhost:5001/health
              '''
            }
            echo "Pruebas de contenedor completadas correctamente."
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        script {
          echo "==== Deploy: DOCKER_AVAILABLE=${env.DOCKER_AVAILABLE} ===="
          if (env.DOCKER_AVAILABLE != "true") {
            echo "Docker no disponible: saltando despliegue."
          } else {
            // Intentar detener contenedor previo (si hay docker CLI disponible en agent esto ayuda; si no, el plugin manejará)
            try {
              sh 'docker stop ${IMAGE_NAME}-prod || true'
              sh 'docker rm ${IMAGE_NAME}-prod || true'
            } catch (err) {
              echo "No se pudo ejecutar docker stop/rm vía shell: ${err}. Continúo con Docker Pipeline API."
            }
            def prod = docker.image("${IMAGE_NAME}:latest").run("-d -p 5000:5000 --name ${IMAGE_NAME}-prod --restart unless-stopped")
            echo "Contenedor productivo lanzado (id): ${prod.id}"
          }
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
      // Guardar artefactos y limpiar workspace local del agente
      archiveArtifacts artifacts: 'models/**', allowEmptyArchive: true
      cleanWs()
    }
  }
}