pipeline{
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'])
        booleanParam(name: 'AUTO_APPROVE', defaultValue: false)
    }

    environment { 
        AWS_REGION = 'us-east-1'
        AWS_ACCESS_KEY_ID = credentials("")
        AWS_SECRET_ACCESS_KEY = credentials('')
        PULUMI_ACCESS_TOKEN = credentials("")
        PULUMI_CI = 'true'
    }

    options{
        timestamps()
    }

    stages{

        stage('Checkout repo'){
            steps { 
                echo 'Cloning repo'
                checkout([
                    $class 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://RandomRepoPage.com/theNameOfTheRepo.git']]
                ])
            }
        }

        stage('Configuring python env'){
            steps{
                echo "Starting the configuration of the python environment"
                sh '''
                    if [ -d pulumi_llm ]; then rm -r pulumi_llm; fi
                    python3 -m venv pulumi_llm
                    source pulumi_llm/bin/activate
                    pip install --upgrade pip
                    pip install pulumi pulumi-aws boto3
                '''
            }
        }

        stage('Pulumi config'){
            steps{
                echo "Pulumi Login"
                sh '''
                    source pulumi_llm/bin/activate
                    pulumi login
                '''
            }
        }

        stage('Pulumi changes'){
            steps{
                echo "Checking configuration that is going to be applied"
                sh '''
                    source pulumi_llm/bin/activate
                    pulumi stack select ${ENVIROMNENT} || pulumi stack init {ENVIRONMENT}
                    pulumi preview --stack ${ENVIRONMENT}
                '''
            }
        }

        stage('deploy pulumi'){
            steps{
                script{
                    if (!params.AUTO_APPROVE){
                        input message: "do you want to deploy the changes to ${params.ENVIRONMENT} environment?"
                    }

                }
                sh '''
                    source pulumi_llm/bin/activate
                    pulumi up --yes --stack ${ENVIRONMENT}
                '''
            }
        }
    }

    post{
        success{
            echo "the Pulumi deployment has been completed successfully in ${params.ENVIRONMENT}"
        }

        failure{
            echo "Deployment failed, check logs for details"
        }
        always{
            sh '''
                deactivate 2>/dev/null || true
                pulumi logout || true
                rm -rf pulumi_llm
            '''
        }
    }


}