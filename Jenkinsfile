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
        PATH = "$HOME/.pulumi/bin:$PATH"
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
                    ls
                '''
            }
        }

        stage('Install Pulumi') {
            steps {
                sh '''
                    if ! command -v pulumi >/dev/null 2>&1; then
                        curl -fsSL https://get.pulumi.com/releases/sdk/pulumi-v3.150.0-linux-x64.tar.gz -o pulumi.tar.gz
                        tar -xzf pulumi.tar.gz
                        mv pulumi/pulumi /usr/local/bin/pulumi
                        chmod +x /usr/local/bin/pulumi
                        rm -rf pulumi pulumi.tar.gz
                    else
                        echo "Pulumi already installed"
                        pulumi version
                    fi
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
                    ./pulumi_llm_env/bin/pip install --upgrade pip
                    ./pulumi_llm_env/bin/pip install pulumi pulumi-aws boto3
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
                        chmod +x ./pulumi_llm_env/bin/pulumi
                        cd pulumi_llm
                        ../pulumi_llm_env/bin/pulumi stack select ${ENVIRONMENT} || echo " stack already exists "
                        ../pulumi_llm_env/bin/pulumi preview
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
                        chmod +x ./pulumi_llm_env/bin/pulumi
                        cd pulumi_llm
                        ../pulumi_llm_env/bin/pulumi up --yes --skip-preview
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
                    chmod +x ./pulumi_llm_env/bin/pulumi
                    cd pulumi_llm
                    ../pulumi_llm_env/bin/pulumi stack select ${ENVIRONMENT}
                    ../pulumi_llm_env/bin/pulumi destroy --yes
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
