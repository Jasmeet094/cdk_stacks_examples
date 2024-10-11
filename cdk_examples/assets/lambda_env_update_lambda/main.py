import json
import boto3
import os
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

functionNames = os.environ['FunctionNames']
functionNamesList = list(functionNames.split(","))

secretArn = os.environ['SecretArn']

lambda_ = boto3.client('lambda')
secret = boto3.client('secretsmanager')


def lambda_handler(event, context):
    # get environment variables from secret
    response = secret.get_secret_value(
        SecretId=secretArn
    )

    # update lambda environment varaibles
    for name in functionNamesList:
        # convert environment variables from string to dictonary
        env = {**json.loads(response['SecretString']), **{"DD_SERVICE": name}, **{"DeploymentEnvironment": name.split("-")[1]}} # noqa
        lambda_.update_function_configuration(
            FunctionName=name,
            Environment={
                'Variables': env
            }
        )
    logger.info(f'Lambda Environment Variables are updated successfully. Functions Name: {functionNames}') # noqa
    return {

        'response': {
            'statusCode': 200,
            'message': json.dumps(f'Lambda Environment Variables are updated Successfully. Function Names: {functionNames}') # noqa
            }
    }
