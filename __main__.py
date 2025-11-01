import pulumi
import pulumi_aws as aws

config = pulumi.Config()
env = config.get("env") or "dev"

role = aws.iam.Role(f"{env}-role", assume_role_policy="""{
                    "Version": 2012-10-17,
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Principal": {"Service": "bedrock.amazonaws.com"},
                            "Efect": "Allow"
                        }
                    ]
                    } """)


aws.iam.RolePolicyAttachment(f"{env}-bedrock-full",
                             role = role.name,
                             policy_arn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess")

lambda_titan = aws.lambda_.Function(f"{env}-titan-func",
                                    role = role.arn,
                                    runtime = "python3.11",
                                    handler="handler.main",
                                    code = pulumi.AssetArchive({
                                        ".": pulumi.FileArchive("./lambda_titan")
                                    }),
                                    environment=aws.lambda_.FunctionEnvironmentArgs(variables={
                                        "MODEL_ID": "amazon.titan-text-lite-v1"
                                    })
                                    )


lambda_claude = aws.lambda_.Function(f"{env}-claude-func",
                                     role = role.arn,
                                     runtime = "python3.11",
                                     handler="handler.main",
                                     code = pulumi.AssetArchive({
                                         ".": pulumi.FileArchive("./lambda_Claude")
                                     }),
                                     environment=aws.lambda_.FunctionEnvironemtArgs(variables={
                                         "MODEL_ID":"anthropic.claude-3.sonnet-20240229-v1:0"
                                     })
                                     )

api = aws.apigatewayv2.Api(f"{env}-api", protocol_type="HTTP")

integration = aws.apigatewayv2.Integration(f"{env}-integ",
                                           api_id = api.id,
                                           integration_type = "AWS_PROXY",
                                           integration_uri = lambda_titan.arn
                                           )

route = aws.apigatewayv2.Route(f"{env}-route",
                               api_id = api.id,
                               route_key = "POST /run",
                               target = pulumi.Output.concat("llm_pulumi/", integration.id))

pulumi.export("api_url", api.api_endpoint)