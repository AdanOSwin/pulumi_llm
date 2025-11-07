import os
import json
import boto3

def main(event, context):
    model_id = os.environ.get("MODEL_ID", "amazon.titan-text-lite-v1")

    prompt = event.get("prompt", "Titan Model")

    client = boto3.client("bedrock-runtime")

    try:
        response = client.invoke_model(
            modelId = model_id,
            contentType = "application/json"
            accept = :"application/json",
            body = json.dumps({"inputText": prompt})
        )

        result = response =["body"].read().decode("utf-8")

        return{
            "statusCode": 200,
            "body": json.dumps({"result": result})
        }
    
    except Exception as e:
        return{
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }