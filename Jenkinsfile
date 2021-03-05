pipeline {
    agent none
    environment {
        REPORT_BUCKET_NAME = credentials('REPORT_BUCKET_NAME')
        GIT_TOKEN = credentials('GIT_TOKEN')
    }
    stages {
        stage('log out python packages') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                sh 'pip freeze'
            }
        }
        stage('pull previous reports from bucket') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                withCredentials([[$class: 'FileBinding', credentialsId:"report_storage_bucket", variable: 'GOOGLE_APPLICATION_CREDENTIALS']]) {
                    sh('python3 $PWD/download_from_bucket.py')
                }
             }
        }
        stage('dynamically create test features') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                sh('python3 $PWD/build_dynamic_tests.py')
             }
        }
        stage('run test features with allure output formatter') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh('behave -f allure_behave.formatter:AllureFormatter -o $PWD/out/allure-results $PWD/features')
                }
             }
        }
        stage('copy in latest category definitions') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                sh('cp ./categories.json $PWD/out/allure-results/categories.json')
            }
        }
        stage('geneate allure report data') {
            agent { docker { image 'frankescobar/allure-docker-service:latest' } }
            steps {
                sh('allure generate $PWD/out/allure-results --clean')
             }
        }
       stage('move report to /out directory') {
            agent { docker { image 'frankescobar/allure-docker-service:latest' } }
            steps {
                sh('cp -a $PWD/allure-report/. $PWD/out/allure-report/')
                sh('rm -rf $PWD/allure-report')
             }
        }
        stage('update report history') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                sh('cp -r $PWD/out/allure-report/history/. $PWD/out/allure-results/history')
             }
        }
        stage('upload updated reports back to bucket') {
            agent { docker { image 'gsscogs/allure-test-generator:latest' } }
            steps {
                withCredentials([[$class: 'FileBinding', credentialsId:"report_storage_bucket", variable: 'GOOGLE_APPLICATION_CREDENTIALS']]) {
                    sh('python3 $PWD/upload_to_bucket.py')
                }
             }
        }
    }
}
