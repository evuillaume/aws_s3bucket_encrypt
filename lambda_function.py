import json
import logging
import os
import boto3
import json
from botocore.exceptions import ClientError

log = logging.getLogger()

# ---------------------------------
def valid_request(event):

    if((event['source'] != "aws.s3") or (event['detail-type'] != 'AWS API Call via CloudTrail')):
        return False

    # Should be present in CloudWatch rule event filter
    #allowed_event_list = []
    #if not(event['detail']['eventName'] in allowed_event_list):
    #    return False

    return True

# ---------------------------------
def check_iam_permission(account, bucket_name):

    bucket_arn = 'arn:aws:s3:::' + bucket_name + '/*'

    lambda_role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::' + account + ':role/S3BucketAutoEncrypt')

    actions = ['s3:PutEncryptionConfiguration', 's3:GetEncryptionConfiguration']

    iam = boto3.client("iam")
    response = iam.simulate_principal_policy(PolicySourceArn=lambda_role_arn, ActionNames=actions, ResourceArns=[ bucket_arn ])
    results = response['EvaluationResults']

    can_encrypt = True
    for actions in results:
        if(actions['EvalDecision'] != 'allowed'):
            action_name = actions['EvalActionName']
            log.critical("Cannot perform " + action_name + " on " + bucket_arn + " because of " + actions['EvalDecision'])
            if action_name == 's3:PutEncryptionConfiguration':
                can_encrypt = False

    return can_encrypt

def lambda_handler(event, context):

    log.error(event)

    s3 = boto3.client('s3')

    bucket_name = event['detail']['requestParameters']['bucketName']

    isValid = valid_request(event)
    if(isValid == False):
        return "Invalid Request: " + event['source'] + "//" + event['detail-type']

    iamAllowed = check_iam_permission(event['account'], bucket_name)
    if(iamAllowed == False):
        return 'IAM Forbiden on bucket ' + bucket_name

    try:
        bucket_tags_dict = s3.get_bucket_tagging(Bucket=bucket_name)
        for tag in bucket_tags_dict["TagSet"]:
            if tag["Key"] == "overrideEncryption":
                if tag["Value"].lower() == "true":
                    return 'Bucket ' + bucket_name + ' has {overrideEncryption} tag set to {True} => pass'
    except:
		pass

    # check for Exception with ServerSideEncryptionConfigurationNotFoundError.
    processEncrypt = False
    try:
        currEncrypt = s3.get_bucket_encryption (Bucket=bucket_name)
        log.error("encryption is in place")
        log.error(currEncrypt)
    except ClientError as e:
		if(e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError'):
		    processEncrypt = True

    if(processEncrypt):
        s3.put_bucket_encryption (Bucket=bucket_name,ServerSideEncryptionConfiguration={'Rules':[{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]})
        log.error('AES-256 has been applied as the default operation after event ' + event['detail']['eventName'] + ' on bucket: ' + bucket_name)

    log.error('Nothing to do...')