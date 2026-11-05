pipeline {
    agent any

    environment {
        APP_NAME        = 'ganesh-devops-project-2'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        TEST_CONTAINER  = "ganesh-smoke-fastapi-${BUILD_NUMBER}"
        HOST_PORT       = "8085"
        PATH            = "C:\\Users\\M THARUN\\AppData\\Local\\Programs\\Python\\Python314;C:\\Users\\M THARUN\\AppData\\Local\\Programs\\Python\\Python314\\Scripts;${env.PATH}"
    }

    options {
        timeout(time: 25, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo "=========================================================="
                echo " [Stage 1] Checking Out Repository: ${APP_NAME}"
                echo "=========================================================="
                checkout scm
            }
        }

        stage('Environment Info') {
            steps {
                echo "=========================================================="
                echo " [Stage 2] Inspecting Build & Runtime Environment"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Host OS: $(uname -a)"
                            python3 --version || python --version
                            docker --version || echo "Docker not available"
                        '''
                    } else {
                        bat '''
                            echo Host Operating System: %OS%
                            python --version
                            docker --version 2>nul || echo Docker not available
                        '''
                    }
                }
            }
        }

        stage('Code Quality & Lint') {
            steps {
                echo "=========================================================="
                echo " [Stage 3] Validating Code Syntax and Compilation"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh 'python3 -m py_compile app/main.py tests/test_main.py'
                    } else {
                        bat 'python -m py_compile app/main.py tests/test_main.py'
                    }
                }
            }
        }

        stage('Execute Unit Tests') {
            steps {
                echo "=========================================================="
                echo " [Stage 4] Running Pytest Suite with JUnit Reporting"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh '''
                            pip3 install pytest fastapi httpx uvicorn aiofiles jinja2 2>/dev/null || pip install pytest fastapi httpx uvicorn aiofiles jinja2
                            pytest -v --junitxml=junit-results.xml tests/
                        '''
                    } else {
                        bat '''
                            pip install pytest fastapi httpx uvicorn aiofiles jinja2 --quiet
                            pytest -v --junitxml=junit-results.xml tests/
                        '''
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'junit-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "=========================================================="
                echo " [Stage 5] Building Docker Image: ${APP_NAME}:${IMAGE_TAG}"
                echo "=========================================================="
                script {
                    def dockerAvailable = false
                    if (isUnix()) {
                        dockerAvailable = (sh(script: 'docker info > /dev/null 2>&1', returnStatus: true) == 0)
                    } else {
                        dockerAvailable = (bat(script: 'docker info > nul 2>&1', returnStatus: true) == 0)
                    }

                    if (dockerAvailable) {
                        echo "Docker daemon is running — building image..."
                        if (isUnix()) {
                            sh "docker build -t ${APP_NAME}:${IMAGE_TAG} -t ${APP_NAME}:latest ."
                        } else {
                            bat "docker build -t ${APP_NAME}:${IMAGE_TAG} -t ${APP_NAME}:latest ."
                        }
                        env.DOCKER_BUILT = 'true'
                    } else {
                        echo "WARNING: Docker daemon is not running. Skipping Docker build."
                        echo "To enable Docker stages: start Docker Desktop and re-run this build."
                        env.DOCKER_BUILT = 'false'
                    }
                }
            }
        }

        stage('Container Smoke Test') {
            when {
                expression { return env.DOCKER_BUILT == 'true' }
            }
            steps {
                echo "=========================================================="
                echo " [Stage 6] Verifying Container Runtime & Health Endpoint"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh """
                            docker run -d --name ${TEST_CONTAINER} -p ${HOST_PORT}:8000 ${APP_NAME}:${IMAGE_TAG}
                            sleep 5
                            curl --fail --retry 5 --retry-delay 2 http://localhost:${HOST_PORT}/health
                        """
                    } else {
                        bat """
                            docker run -d --name %TEST_CONTAINER% -p %HOST_PORT%:8000 %APP_NAME%:%IMAGE_TAG%
                            powershell -Command "Start-Sleep -Seconds 5"
                            powershell -Command "Invoke-WebRequest -Uri http://localhost:%HOST_PORT%/health -UseBasicParsing | Select-Object -ExpandProperty Content"
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo "=========================================================="
            echo " Post-Build: Cleaning Up Ephemeral Smoke Test Container"
            echo "=========================================================="
            script {
                try {
                    if (isUnix()) {
                        sh """
                            docker stop ${TEST_CONTAINER} 2>/dev/null || true
                            docker rm -f ${TEST_CONTAINER} 2>/dev/null || true
                        """
                    } else {
                        bat """
                            docker stop %TEST_CONTAINER% 2>nul
                            docker rm -f %TEST_CONTAINER% 2>nul
                            exit /b 0
                        """
                    }
                } catch (err) {
                    echo "Cleanup skipped (Docker not running): ${err}"
                }
            }
        }
        success {
            echo "=========================================================="
            echo " BUILD SUCCESSFUL: ${APP_NAME}:${IMAGE_TAG} is ready!"
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo " BUILD FAILED: Review the stage logs above for errors."
            echo "=========================================================="
        }
    }
}
