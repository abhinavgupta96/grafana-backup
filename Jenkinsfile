#!groovy

pipeline {
  triggers {
    cron('H 0 * * *')
  }
  agent {
    label "base"
  }
  
  options {
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
  }
   environment {
        BITBUCKET_COMMON_CREDS = credentials('<bit_bucket_token>')
        GRAFANA_TOKEN = credentials('<grafana_token>')

    }
  stages {
     stage('Checkout SCM')
     {
         steps{
             deleteDir()
             checkout scm
         }
     }
     stage('grafana-backup') {
       steps {
           
           script {
               withEnv(["HOME=${env.WORKSPACE}"]) {
                  docker.image('python:3.11.0a5-alpine3.14').inside('-u root') {
                      sh 'env'
                      sh 'apk update && apk upgrade && apk add git'
                      sh 'git config --global user.email "$<Bitbucket_email>"'
                      sh 'git config --global user.name "$<Bitbucket_username>"'
                      sh 'python3 -m pip install --user --upgrade pip setuptools wheel'
                      sh 'python3 -m pip install --user -r requirements.txt'
                      sh 'grafana_token=$GRAFANA_TOKEN bit_bucket_username=$BITBUCKET_COMMON_CREDS_USR bit_bucket_token=$BITBUCKET_COMMON_CREDS_PSW python3 main.py'                   
               }

           }
      }    
     }
     }
 }
 
}