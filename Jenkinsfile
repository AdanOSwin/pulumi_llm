pipeline {
    agent any

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'])
        booleanParam(name: 'AUTO_APPROVE', defaultValue: false)
        booleanParam(name: 'DESTROY', defaultValue: false, description: "Destroy infra")
    }

    environment { 
        AWS_REGION = 'us-east-1'
        PULUMI_ACCESS_TOKEN = credentials("pulumi_token")
        PULUMI_CI = 'true'
        PATH = "$WORKSPACE/pulumi_llm/bin:$PATH"
    }

    options {
        timestamps()
    }

    stages {

        stage('Check python venv'){
            steps {
                sh '''
                    if ! dpkg -s python3-venv >/dev/null 2>&1; then
                        echo "instalando python venv"
                        sudo apt update
                        sudo apt install -y python3-venv
                    else
                        echo "python3-venv ya existe"
                    fi
                '''
            }
        }

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
                    python3 -m venv llm
                    . llm/bin/activate
                    pip install --upgrade pip
                    pip install pulumi pulumi-aws boto3
                    deactivate
                '''
            }
        }

        stage('Pulumi config') {
            steps {
                withAWS(credentials: 'aws_credentials', region: "${AWS_REGION}") {
                    echo "Pulumi Login"
                    sh '''
                        . llm/bin/activate

                        echo "######################## $WORKSPACE ##########################"
                        
                        echo "##################################"
                        echo "######################################"
                        pwd 
                        ls -la 
                        echo "########################################"
                        echo "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
                        ls -la llm/

                        echo "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"

                        pulumi stack select ${ENVIRONMENT} || pulumi stack init ${ENVIRONMENT}
                        pulumi preview
                        deactivate
                    '''
                }
            }
        }

        stage('deploy pulumi') {
            when { expression { return params.DESTROY == false }}
            steps {
                withAWS(credentials: 'aws_credentials', region: "${AWS_REGION}") {
                    echo "deploying infra"
                    sh '''
                        cd llm
                        . llm/bin/activate
                        pulumi up --yes --skip-preview
                        deactivate
                    '''
                }
            }
        }

        stage('pulumi destroy'){
            when {
                expression {return params.DESTROY == true}
            }
            steps {
                withAWS(credentials: 'aws_credentials', region: "${AWS_REGION}")
                echo "DEstroying infra"
                sh '''
                    cd llm
                    . llm/bin/activate
                    pulumi stack select ${ENVIRONMENT}
                    pulumi destroy --yes
                    deactivate
                '''
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
                rm -rf llm
            '''
        }
    }
}
