## Cake Ordering System

##### This is the python version of the serverless aws application, built in the [LinkedIn course](https://www.linkedin.com/learning-login/share?forceAccount=false&redirect=https%3A%2F%2Fwww.linkedin.com%2Flearning%2Faws-for-developers-data-driven-serverless-applications-with-kinesis%3Ftrk%3Dshare_ent_url%26shareId%3DiP%252BBsrDHS1uD2iNJ9F5bwQ%253D%253D&account=2113185)

### Description:
This is the cake ordering system. System starts with HTTP trigger to lambda function for the new order. 
Function creates new order, places it into the DynamoDB and Kinesis Stream.
Another lambda is waiting for the new event from Kinesis and notifies cake producers via Email about new order.
When the cake is ready, cake producer sends HTTP trigger to fulfill the order for the client. Lambda searches the order in the DynamoDB,
riches it with fulfilled information, updates it and sends to SQS. 
When lambda with SQS Trigger received notification, it can notify delivery company via HTTP Rest about order.
When order is delivered, order company sends HTTP trigger to another lambda. This function search for the order in the DynamoDB,
updates it with delivery information and sends delivery information into the another SQS Stream.
Last lambda listen for the SQS Stream with delivery information and sends feedback to the delivery company.

HTTP -> Lambda -> Dynamo (New Order), Kinesis (New Order)
Kinesis (New Order) -> Lambda -> SES (Email notification)

HTTP -> Lambda -> Dynamo (Fulfill Order), Kinesis (Fulfill Order)
Kinesis (Fulfill Order) -> Lambda -> Dynamo (SendForDelivery Order), SQS (SendForDelivery Order)
SQS (SendForDelivery Order) -> Lambda (Notify delivery company)

HTTP -> Lambda -> Dynamo (Delivered Order), SQS (Review Delivery)
SQS (Review Delivery) -> Lambda (Notify delivery company) 

This service built with the help of:
- [Python3](https://www.python.org/downloads/)
- [NPM](https://www.npmjs.com/get-npm)
- [AWS](https://aws.amazon.com/)
- [Serverless](https://www.serverless.com/)
- [AWS lambda](https://aws.amazon.com/ru/lambda/)
- [AWS Kinesis](https://aws.amazon.com/ru/kinesis/)
- [AWS DynamoDB](https://aws.amazon.com/ru/dynamodb/)
- [AWS SQS](https://aws.amazon.com/ru/sqs/)
- [AWS SES](https://aws.amazon.com/ru/ses/)

To run this project on your amazon environment you need to:
- install npm
- install npm **serverless**
- install npm **serverless-pseudo-parameters**
- install npm **serverless-python-requirements**
- configure aws credentials
- create aws python3 template
- setup serverless.yml (already filled in the project)
- deploy project to aws (sls deploy)
- configure Amazon Simple Email Service for emails, provided in the serverless.yml 

