#The OTP is entered by the visitor. And the OTP is matched with the corresponding OTP in the database.
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    otp_table_name = 'passcodes'
    app_region = 'us-west-2'
    dynamodb= boto3.resource('dynamodb',region_name=app_region)
    otp_table= dynamodb.Table(otp_table_name)
    #print(event['message'])
    responseData = otp_table.query(IndexName="otp-index", KeyConditionExpression=Key('otp').eq(str(event['message'])))
    #print(responseData)
    item_list = responseData["Items"]
    uName = ""
    faceId = ""
    response_body = {}

    for item in item_list:
        faceId = str(item["faceId"])
    #print ("Faceid: " + faceId)
        
    if responseData and len(responseData['Items']) >= 1:
        visitor_name = get_visitor_name(faceId)
        response_body['faceId'] = faceId
        response_body['visitorName'] = visitor_name
        #json_data = json.loads(response_body)
        return {
        'statusCode': 200,
        'body': response_body
        }

    return {
        'statusCode': 400,
        'body': "Invalid OTP"
    }

def get_visitor_name(faceId):
    visitor_table_name = 'visitors'
    app_region = 'us-west-2'
    dynamodb= boto3.resource('dynamodb',region_name=app_region)
    print(faceId)
    visitor_table = dynamodb.Table(visitor_table_name)
    visitorResponseData = visitor_table.query(KeyConditionExpression=Key('faceId').eq(faceId))
    print (visitorResponseData)
    item_list = visitorResponseData["Items"]
    
    visitor_data = item_list[0]
    visitor_name = visitor_data["name"]
    return visitor_name    
