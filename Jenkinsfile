pipeline {
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment{
        registry = 'khoapham99/nsfw-det-app'
        registryCredential = 'dockerhub'      
    }

    stages {
        stage('Test') {
            steps {
                echo "Checking USER"
                echo $USER
                // sh 'pytest test_logic.py'
            }
            agent {
                docker {
                    image 'khoapham99/nsfw-det-app:latest' 
                }
            }
            // steps {
            //     echo 'Testing model correctness..'
            //     sh 'pytest test_logic.py'
            // }
        }
        stage('Build') {
            steps {
                script {
                    echo 'Building image for deployment..'
                    dockerImage = docker.build registry + ":$BUILD_NUMBER" 
                    echo 'Pushing image to dockerhub..'
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying models..'
                echo 'Running a script to trigger pull and start a docker container'
            }
        }
    }
}