pipeline {
    agent { docker { image 'gsscogs/allure-test-generator:latest' } }
    stages {
        stage('check dependencies') {
            steps {
                sh 'pip freeze'
            }
        },
        stage('pull data from bucket') {
            steps {
                sh 'python3 ./download_from_bucket.py'
            }
        }
    }
}
