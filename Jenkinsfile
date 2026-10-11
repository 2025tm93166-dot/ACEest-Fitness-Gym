pipeline {
    agent any
    triggers {
        pollSCM('* * * * *')
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out the configured SCM revision'
                checkout scm
                echo 'Checkout complete'
            }
        }

        stage('Set Up Python Environment') {
            steps {
                echo 'Creating Python virtual environment using python3'
                sh 'python3 -m venv .venv'
                echo 'Python virtual environment created'
            }
        }

        stage('Build') {
            steps {
                echo 'Upgrading pip'
                sh '.venv/bin/python -m pip install --upgrade pip'
                echo 'Installing project dependencies from requirements.txt'
                sh '.venv/bin/python -m pip install -r requirements.txt'
                echo 'Dependency installation complete'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Creating directory for test reports'
                sh 'mkdir -p reports'
                echo 'Running pytest suite and generating JUnit report'
                sh '.venv/bin/python -m pytest tests/test_app.py -q --junitxml=reports/pytest.xml'
                echo 'Tests completed'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image aceest-fitness'
                sh 'docker build -t aceest-fitness .'
                echo 'Docker image build complete'
            }
        }
    }

    post {
        always {
            echo 'Publishing JUnit test report'
            junit testResults: 'reports/pytest.xml', allowEmptyResults: true
        }
    }
}
