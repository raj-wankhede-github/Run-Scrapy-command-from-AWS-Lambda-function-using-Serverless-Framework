import boto3
import json
import os
from loguru import logger


# AWS Configurations
access_key = os.getenv("ACCESS_KEY")
secret_access_key = os.getenv("SECRET_ACCESS_KEY")
table_name = os.getenv("TABLE_NAME")


# DynamoDB Client
DYNAMODB_CLIENT = boto3.client(
    service_name="dynamodb",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access_key,
    region_name="us-east-1",
)


class DynamoDBOperations:
    def __init__(self) -> None:
        pass

    def dynamodb_put_item(self, input_data: dict):
        try:
            DYNAMODB_CLIENT.put_item(TableName=table_name, Item=input_data)
        except Exception as exc:
            logger.exception(exc)
