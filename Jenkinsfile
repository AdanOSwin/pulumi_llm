pipeline{
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'])
        booleanParam(name: 'AUTO_APPROVE', defaultValue: false)
    }

    environment { 
        AWS_REGION = 'us-east-1'
        //#AWS_ACCESS_KEY_ID = credentials("")
        //AWS_SECRET_ACCESS_KEY = credentials('')
        PULUMI_ACCESS_TOKEN = credentials("pulumi_token")
        PULUMI_CI = 'true'
        PATH = "$WORKSPACE/venv/bin:$PATH"
    }

    options{
        timestamps()
    }

    stages{

        stage('Remove previous workspace'){
            steps {
                "Removing previous python environment"
                sh 'if [ -d venv]; then rm -rf venv; fi'
                deleteDir()
            }
        }

        //stage('Checkout repo'){
        //    steps { 
        //        echo 'Cloning repo'
        //        checkout([
        //            $class 'GitSCM',
        //            branches: [[name: '*/main']],
        //            userRemoteConfigs: [[url: 'https://RandomRepoPage.com/theNameOfTheRepo.git']]
        //        ])
        //    }
        //}

        stage('Python env'){
            steps{
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

        stage('Pulumi config'){
            steps{
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

        //stage('Pulumi changes'){
        //    steps{
        //        echo "Checking configuration that is going to be applied"
        //        sh '''
        //            source pulumi_llm/bin/activate
        //            pulumi stack select ${ENVIROMNENT} || pulumi stack init {ENVIRONMENT}
        //            pulumi preview --stack ${ENVIRONMENT}
        //        '''
        //    }
        //}

        stage('deploy pulumi'){
            steps{
                withAWS(credentials: 'aws_credentials', region: "${AWS_DEFAULT_REGION}"){
                    echo "deploying infra"
                    sh '''
                        source pulumi_llm/bin/activate
                        pulumi up --yes --skip-preview
                        deactivate
                        '''
                }   
                //script{
                //    if (!params.AUTO_APPROVE){
                //        input message: "do you want to deploy the changes to ${params.ENVIRONMENT} environment?"
                //    }

                //}
                //sh '''
                //    source pulumi_llm/bin/activate
                //    pulumi up --yes --stack ${ENVIRONMENT}
                //'''
            //}
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