
import json
import sys
sys.path.insert(1, '/opt')
import cv2
import boto3
import base64
from botocore.vendored import requests
import random
import time

def lambda_handler(event, context):
    # TODO implement
    kvs_client = boto3.client('kinesisvideo')
    kvs_data_pt = kvs_client.get_data_endpoint(
    StreamARN='arn:aws:kinesisvideo:us-west-2:410179727992:stream/LiveRekognitionVideoAnalysisBlog/1573073469067', # kinesis stream arn
    APIName='GET_MEDIA'
    )
    
    print(kvs_data_pt)
    
    end_pt = kvs_data_pt['DataEndpoint']
    kvs_video_client = boto3.client('kinesis-video-media', endpoint_url=end_pt, region_name='us-west-2') # provide your region
    record = event['Records'][0]
    payload = base64.b64decode(record["kinesis"]["data"])
    payload_obj=json.loads(payload)
    frag_num = payload_obj["InputInformation"]["KinesisVideo"]["FragmentNumber"]
    kvs_stream = kvs_video_client.get_media(
        StreamARN='arn:aws:kinesisvideo:us-west-2:410179727992:stream/LiveRekognitionVideoAnalysisBlog/1573073469067', # kinesis stream arn
        StartSelector={'StartSelectorType': 'FRAGMENT_NUMBER', 'AfterFragmentNumber': frag_num} 
    )
    print(kvs_stream)

    with open('/tmp/streams.mkv', 'wb') as f:
        streamBody = kvs_stream['Payload'].read(1024*2048) # can tweak this
        f.write(streamBody)
        # use openCV to get a frame
        cap = cv2.VideoCapture('/tmp/streams.mkv')

        # use some logic to ensure the frame being read has the person, something like bounding box or median'th frame of the video etc
        ret, frame = cap.read() 
        cv2.imwrite('/tmp/frame.jpg', frame)
        s3_client = boto3.client('s3')
        s3_client.upload_file(
            '/tmp/frame.jpg',
            'uploadbucket123', # replace with your bucket name
            'frame.jpg'
        )
        cap.release()
        print('Image uploaded')

    rekognition = boto3.client('rekognition')
    #source_response = requests.get('https://rekognitionbucket11.s3-us-west-2.amazonaws.com/neel.jpg')
    #source_response_content = source_response.content
    s3 = boto3.resource(service_name='s3')
    bucket = s3.Bucket('rekognitionbucket11')
    target_response = requests.get('https://uploadbucket123.s3-us-west-2.amazonaws.com/frame.jpg')
    target_response_content = target_response.content
    print(target_response_content)

    recognized_image_key = ''
    faceId = ''
    collectionId = 'rekVideoBlog'
    confidence = 0
    for obj in bucket.objects.all():
        # Compare frame captured from webcam to the image in S3 bucket.
        #print (obj.name)
        recognized_image_key = obj.key
        print (obj.key)
        url = "https://{0}.s3-us-west-2.amazonaws.com/{1}".format("rekognitionbucket11", obj.key)
        print (url)
        source_response = requests.get(url)
        source_response_content = source_response.content
        rekognition_response = rekognition.compare_faces(SourceImage={'Bytes': source_response_content}, TargetImage={'Bytes': target_response_content}) 

        rekognition_index_response = rekognition.index_faces(CollectionId=collectionId, Image={ 'S3Object': {'Bucket':'rekognitionbucket11','Name':recognized_image_key} })
        for faceRecord in rekognition_index_response['FaceRecords']:
         faceId = faceRecord['Face']['FaceId']

        for faceMatch in rekognition_response['FaceMatches']:
            confidence = int(faceMatch['Face']['Confidence'])
        
        if confidence>70:
            break

        print (rekognition_response)
    
    

    for faceMatch in rekognition_response['FaceMatches']:
        confidence = int(faceMatch['Face']['Confidence'])

    #ses = boto3.client('ses')
    if confidence and confidence>70:
        print("faces MATCHHH")
        otp=""
        for i in range(6):
            otp+=str(random.randint(1,9))
        print ("One Time Password is ")
        print (otp)
        expirationTime = time.time() + 300 #5 min TTL

        dynamo_client = boto3.resource('dynamodb')
        otp_table = dynamo_client.Table('passcodes')

        otp_table.put_item(
            Item={
                "faceId" : faceId,
                "otp" : otp,
                "expirationTime" : int(expirationTime)} 
        )

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

    else:
        print("faces dont MATCHH")
        topic_arn = "arn:aws:sns:us-west-2:410179727992:new_visitor"
        sns = boto3.client("sns")
        msg = "1 unknown visitor " + "https://uploadbucket123.s3-us-west-2.amazonaws.com/frame.jpg" + "\n To allow access enter details in the link " + "http://addvisitorui.s3-website-us-west-2.amazonaws.com/"
        sub = "Unknown Visitor Alert"
        response = sns.publish(
        TopicArn=topic_arn,
        Message=msg,
        Subject=sub
        ) 

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }