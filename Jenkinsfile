pipeline {
    agent any
    environment {
    }
    stages {
        stage('Generate Docs') {
            steps {
                sh 'create_docs.py'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}