pipeline {
    agent any

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'])
        booleanParam(name: 'AUTO_APPROVE', defaultValue: false)
    }

    environment { 
        AWS_REGION = 'us-east-1'
        PULUMI_ACCESS_TOKEN = credentials("pulumi_token")
        PULUMI_CI = 'true'
        PATH = "$WORKSPACE/venv/bin:$PATH"
    }

    options {
        timestamps()
    }

    stages {

        stage('Remove previous workspace') {
            steps {
                echo 'Removing previous python environment'
                sh 'if [ -d venv ]; then rm -rf venv; fi'
                deleteDir()
            }
        }

        stage('Python env') {
            steps {
                echo "Starting the configuration of the python environment"
                sh '''
                    python3 -m venv pulumi_llm
                    source pulumi_llm/bin/activate
                    pip install --upgrade pip
                    pip install pulumi pulumi-aws boto3
                    deactivate
                '''
            }
        }

        stage('Pulumi config') {
            steps {
                withAWS(credentials: 'aws_credentials', region: "${AWS_DEFAULT_REGION}") {
                    echo "Pulumi Login"
                    sh '''
                        source pulumi_llm/bin/activate
                        pulumi stack select ${ENVIRONMENT} || pulumi stack init ${ENVIRONMENT}
                        pulumi preview
                        deactivate
                    '''
                }
            }
        }

        stage('deploy pulumi') {
            steps {
                withAWS(credentials: 'aws_credentials', region: "${AWS_DEFAULT_REGION}") {
                    echo "deploying infra"
                    sh '''
                        source pulumi_llm/bin/activate
                        pulumi up --yes --skip-preview
                        deactivate
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "The Pulumi deployment has been completed successfully in ${params.ENVIRONMENT}"
        }

        failure {
            echo "Deployment failed, check logs for details"
        }

        always {
            sh '''
                deactivate 2>/dev/null || true
                pulumi logout || true
                rm -rf pulumi_llm
            '''
        }
    }
}
