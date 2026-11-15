#!/bin/bash
set -e

awslocal s3 mb s3://urbanmove-datalake

TOPIC_ARN=$(awslocal sns create-topic --name urbanmove-events --query 'TopicArn' --output text)

MAINT_DLQ_URL=$(awslocal sqs create-queue --queue-name maintenance-dlq --query 'QueueUrl' --output text)
MAINT_DLQ_ARN=$(awslocal sqs get-queue-attributes --queue-url "$MAINT_DLQ_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)

MAINT_QUEUE_URL=$(awslocal sqs create-queue --queue-name maintenance-queue \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$MAINT_DLQ_ARN\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}" \
  --query 'QueueUrl' --output text)
MAINT_QUEUE_ARN=$(awslocal sqs get-queue-attributes --queue-url "$MAINT_QUEUE_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)

RELOC_QUEUE_URL=$(awslocal sqs create-queue --queue-name relocation-queue --query 'QueueUrl' --output text)
RELOC_QUEUE_ARN=$(awslocal sqs get-queue-attributes --queue-url "$RELOC_QUEUE_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)

DL_QUEUE_URL=$(awslocal sqs create-queue --queue-name datalake-ingestion-queue --query 'QueueUrl' --output text)
DL_QUEUE_ARN=$(awslocal sqs get-queue-attributes --queue-url "$DL_QUEUE_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)

awslocal sns subscribe --topic-arn "$TOPIC_ARN" --protocol sqs --notification-endpoint "$MAINT_QUEUE_ARN"
awslocal sns subscribe --topic-arn "$TOPIC_ARN" --protocol sqs --notification-endpoint "$RELOC_QUEUE_ARN"
awslocal sns subscribe --topic-arn "$TOPIC_ARN" --protocol sqs --notification-endpoint "$DL_QUEUE_ARN"