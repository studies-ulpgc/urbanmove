#!/bin/bash
awslocal s3 mb s3://urbanmove-datalake
awslocal sns create-topic --name urbanmove-events
awslocal sqs create-queue --queue-name maintenance-queue
awslocal sqs create-queue --queue-name maintenance-dlq
awslocal sqs create-queue --queue-name datalake-ingestion-queue