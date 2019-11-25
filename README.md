# Smart-Door---Amazon-Kinesis
## DESCRIPTION
•	The project uses Kinesis Video Streams and Amazon Rekognition to build a distributed system that authenticates people and provides them with access to a virtual door.

•	We index each visitor by the FaceId detected by Amazon Rekognition2, alongside the name of the visitor and their phone number. When storing a new face, if the FaceId returned by Rekognition already exists in the database, then the new photo is appended to the existing photos array.

•	A Kinesis Video Stream3 is developed to capture and stream video for analysis. For every known face detected by Rekognition,we send the visitor an SMS message to the phone number on file. The text message should include a PIN or a One-Time Passcode (OTP) that they can use to open the virtual door.

•	For every unknown face detected by Rekogniton, send an SMS to the “owner” a photo of the visitor. The text message should also include a link to approve access for the visitor.
## ABOUT
This project is a part of the project component for the course- Cloud Computing and Applications (CS-GY 9223, New York University) 
## Authors: Indraneel Ray , Hemanth Teja, Vivek Kumar & Durga Prasad
## ARCHITECHTURE :- 
 ![alt text](https://github.com/HemanthTejaY/Smart-Door---Amazon-Kinesis/blob/master/Architecture/architecture-kinesis.JPG)



