pipeline {
    agent { docker { image 'gsscogs/allure-test-generator:latest' } }
    environment {
        REPORT_BUCKET_NAME = credentials('REPORT_BUCKET_NAME')
        GIT_TOKEN = credentials('GIT_TOKEN')
    }
    stages {
        stage('check dependencies') {
            steps {
                sh 'pip freeze'
            }
        }
        stage('pull previous reports from bucket') {
            steps {
                withCredentials([[$class: 'FileBinding', credentialsId:"report_storage_bucket", variable: 'GOOGLE_APPLICATION_CREDENTIALS']]) {
                    sh('python3 ./download_from_bucket.py')
                }
             }
        }
        stage('create dynamic features') {
            steps {
                sh('python3 ./build_dynamic_tests.py')
             }
        }
    }
}
