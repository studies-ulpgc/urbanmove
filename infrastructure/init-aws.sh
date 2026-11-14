#!/bin/bash
awslocal s3 mb s3://urbanmove-datalake
awslocal sns create-topic --name urbanmove-events
awslocal sqs create-queue --queue-name maintenance-queue
awslocal sqs create-queue --queue-name maintenance-dlq
awslocal sqs create-queue --queue-name datalake-ingestion-queue
awslocal sns subscribe --topic-arn arn:aws:sns:us-east-1:000000000000:urbanmove-events --protocol sqs --notification-endpoint arn:aws:sqs:us-east-1:000000000000:maintenance-queue
awslocal sns subscribe --topic-arn arn:aws:sns:us-east-1:000000000000:urbanmove-events --protocol sqs --notification-endpoint arn:aws:sqs:us-east-1:000000000000:datalake-ingestion-queue