pipeline {
    agent { docker { image 'gsscogs/allure-test-generator:latest' } }
    environment {
        REPORT_BUCKET_NAME = credentials('REPORT_BUCKET_NAME')
        GIT_TOKEN = credentials('GIT_TOKEN')
    }
    stages {
        stage('log out python packages') {
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
        stage('dynamically create test features') {
            steps {
                sh('python3 ./build_dynamic_tests.py')
             }
        }
        stage('run test features with allure output formatter') {
            steps {
                sh('behave -f allure_behave.formatter:AllureFormatter -o allure-results ./features')
             }
        }
    }
}
