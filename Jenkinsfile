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

        //stage('clean workspace'){
        //    steps{
        //        sh '''
        //            rm -rf pulumi pulumi_llm __pycache

        //            find . -type d -name "__pycache__" -exec rm -rf {} +
        //        '''
        //    }
        //}
        stage('Checkout'){
            steps{
                echo "CLoning repo"
                checkout scm
                sh '''
                    ls -la
                '''
            }
        }

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

        //stage('DElete previous workspace') {
        //    steps {
        //        echo 'Removing previous python environment'
        //        sh 'if [ -d venv ]; then rm -rf venv; fi'
        //        deleteDir()
        //    }
        //}

        stage('Python env') {
            steps {
                echo "Starting the configuration of the python environment"
                sh '''
                    python3 -m venv pulumi_llm_env
                    . pulumi_llm_env/bin/activate
                    pip install --upgrade pip
                    pip install pulumi pulumi-aws boto3
                    deactivate
                '''
            }
        }

        //stage('DEBUG'){
        //    steps{
        //        sh '''
        //            echo "PATH: $(pwd)"
        //            echo "FILES:"
        //            ls -la
        //        '''
        //    }
        //}

        stage('Pulumi config') {
            steps {
                withAWS(credentials: 'aws_credentials', region: "${AWS_REGION}") {
                    echo "Pulumi Login"
                    sh '''
                        . pulumi_llm_env/bin/activate
                        cd pulumi_llm
                        echo "######################## $WORKSPACE ##########################"
                        pwd
                        echo "##################################"
                        echo "######################################"
                        pwd 
                        ls -la 
                        echo "########################################"

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
                        . pulumi_llm_env/bin/activate
                        cd pulumi_llm
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
                    . pulumi_llm_env/bin/activate
                    cd pulumi_llm
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
                rm -rf pulumi_llm
            '''
        }
    }
}
