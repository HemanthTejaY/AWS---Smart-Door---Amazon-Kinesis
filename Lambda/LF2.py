import json
import boto3
from botocore.vendored import requests
import time
import random

def lambda_handler(event, context):
    name = event['name']
    number = event['number']

    collectionId = 'rekVideoBlog'
    frame_name = "frame.jpg"

    rekognition = rekognition = boto3.client('rekognition')
    try:
        rekognition_index_response = rekognition.index_faces(CollectionId=collectionId, Image={'S3Object': {'Bucket':'uploadbucket123','Name':frame_name}},
                                    ExternalImageId=frame_name,
                                    MaxFaces=1,
                                    QualityFilter="AUTO",
                                    DetectionAttributes=['ALL'])
    except:
        return {
        'statusCode': 500,
        'body': 'Internal Server Error'
    }

    faceId = ''
    for faceRecord in rekognition_index_response['FaceRecords']:
         faceId = faceRecord['Face']['FaceId']
    
    print(faceId)
    
    dynamo_client = boto3.resource('dynamodb')
    visitor_table = dynamo_client.Table('visitors')    

    rekognition_bucket = "rekognitionbucket11"
    photos = []
    photo_dict = {}
    object_key = str(faceId) + str(name) + ".jpg"
    bucket = rekognition_bucket
    createdTimeStamp = int(time.time())
    photo_dict["objectKey"] = object_key
    photo_dict["bucket"] = bucket
    photo_dict["createdTimeStamp"] = createdTimeStamp
    
    photos.append(photo_dict)

    visitor_table.put_item(
        Item={
                "name": name,
                "faceId" : faceId,
                "phoneNumber" : number,
                "photos" : photos
            } 
    )

    s3 = boto3.resource('s3')
    copy_source = {
      'Bucket': 'uploadbucket123',
      'Key': frame_name
    }
    known_visitors_bucket = s3.Bucket('rekognitionbucket11')
    known_visitors_bucket.copy(
            copy_source, object_key
        )

    otp = generate_otp(faceId, int(time.time()+30))
    send_sns(otp)

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def generate_otp(faceId, expirationTime):
    dynamo_client = boto3.resource('dynamodb')
    otp_table = dynamo_client.Table('passcodes')

    otp=""
    for i in range(6):
        otp+=str(random.randint(1,9))

    otp_table.put_item(
        Item={
            "uName": "Visitor",
            "faceId" : faceId,
            "otp" : otp,
            "expirationTime" : int(expirationTime)} 
    )

    return otp

def send_sns(otp):
    topic_arn = "arn:aws:sns:us-west-2:410179727992:returning_visitor"
    sns = boto3.client("sns")
    msg = "Your One Time Password is " + str(otp) + " Enter it in this link.  " + "http://visitorui.s3-website-us-west-2.amazonaws.com"
    sub = "Your Smart Gate OTP"
    response = sns.publish(
    TopicArn=topic_arn,
    Message=msg,
    Subject=sub
    ) 
    print("sns sent" + json.dumps(response))