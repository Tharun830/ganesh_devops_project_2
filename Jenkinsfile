pipeline {
    agent any

    environment {
        APP_NAME        = 'ganesh-devops-project-2'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        TEST_CONTAINER  = "ganesh-smoke-fastapi-${BUILD_NUMBER}"
        HOST_PORT       = "8085"
        // Ensure Python and Pip are accessible to Jenkins on Windows agent environments
        PATH            = "C:\\Users\\M THARUN\\AppData\\Local\\Programs\\Python\\Python314;C:\\Users\\M THARUN\\AppData\\Local\\Programs\\Python\\Python314\\Scripts;${env.PATH}"
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "=========================================================="
                echo "🚀 [Stage 1] Checking Out Repository: ${APP_NAME}"
                echo "=========================================================="
                checkout scm
            }
        }

        stage('Environment Info') {
            steps {
                echo "=========================================================="
                echo "🔍 [Stage 2] Inspecting Build & Runtime Environment"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Host OS: $(uname -a)"
                            python3 --version || python --version
                            docker --version
                        '''
                    } else {
                        bat '''
                            echo Host Operating System: %OS%
                            python --version
                            docker --version
                        '''
                    }
                }
            }
        }

        stage('Code Quality & Lint') {
            steps {
                echo "=========================================================="
                echo "🧹 [Stage 3] Validating Code Syntax and Compilation"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m py_compile app/main.py tests/test_main.py
                        '''
                    } else {
                        bat '''
                            python -m py_compile app/main.py tests/test_main.py
                        '''
                    }
                }
            }
        }

        stage('Execute Unit Tests') {
            steps {
                echo "=========================================================="
                echo "🧪 [Stage 4] Running Pytest Suite with JUnit Reporting"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh '''
                            pip3 install pytest httpx || pip install pytest httpx
                            pytest -v --junitxml=junit-results.xml tests/
                        '''
                    } else {
                        bat '''
                            pip install pytest httpx
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
                echo "🐳 [Stage 5] Building Docker Image: ${APP_NAME}:${IMAGE_TAG}"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh """
                            docker build -t ${APP_NAME}:${IMAGE_TAG} -t ${APP_NAME}:latest .
                        """
                    } else {
                        bat """
                            docker build -t ${APP_NAME}:${IMAGE_TAG} -t ${APP_NAME}:latest .
                        """
                    }
                }
            }
        }

        stage('Container Smoke Test') {
            steps {
                echo "=========================================================="
                echo "🔬 [Stage 6] Verifying Container Runtime & Health Endpoint"
                echo "=========================================================="
                script {
                    if (isUnix()) {
                        sh """
                            docker run -d --name ${TEST_CONTAINER} -p ${HOST_PORT}:8000 ${APP_NAME}:${IMAGE_TAG}
                            sleep 4
                            curl --fail --retry 5 --retry-delay 2 http://localhost:${HOST_PORT}/health
                        """
                    } else {
                        bat """
                            docker run -d --name ${TEST_CONTAINER} -p ${HOST_PORT}:8000 ${APP_NAME}:${IMAGE_TAG}
                            powershell -Command "Start-Sleep -Seconds 4; curl.exe --fail --retry 5 --retry-delay 2 http://localhost:${HOST_PORT}/health"
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo "=========================================================="
            echo "🧹 Post-Build: Cleaning Up Ephemeral Smoke Test Container"
            echo "=========================================================="
            script {
                if (isUnix()) {
                    sh """
                        docker stop ${TEST_CONTAINER} || true
                        docker rm -f ${TEST_CONTAINER} || true
                    """
                } else {
                    bat """
                        docker stop ${TEST_CONTAINER} 2>nul || exit /b 0
                        docker rm -f ${TEST_CONTAINER} 2>nul || exit /b 0
                    """
                }
            }
        }
        success {
            echo "=========================================================="
            echo "✅ BUILD SUCCESSFUL: Artifact ${APP_NAME}:${IMAGE_TAG} is ready!"
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo "❌ BUILD FAILED: Review the stage logs above for errors."
            echo "=========================================================="
        }
    }
}
