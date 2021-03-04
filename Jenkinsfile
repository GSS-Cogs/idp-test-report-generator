pipeline {
    agent { docker { image 'gsscogs/allure-test-generator:latest' } }
    stages {
        stage('check dependencies') {
            steps {
                sh 'pip freeze'
            }
        }
    }
}
