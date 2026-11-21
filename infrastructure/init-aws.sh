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

apt-get update -qq && apt-get install -y -qq zip > /dev/null

mkdir -p /tmp/lambdas
cd /workspace
zip -rq /tmp/lambdas/maintenance_detection.zip shared/
(cd lambdas/maintenance_detection && zip -rq /tmp/lambdas/maintenance_detection.zip handler.py)

zip -rq /tmp/lambdas/relocation.zip shared/
(cd lambdas/relocation && zip -rq /tmp/lambdas/relocation.zip handler.py)

awslocal lambda create-function \
  --function-name maintenance-detection-lambda \
  --runtime python3.11 \
  --handler handler.lambda_handler \
  --zip-file fileb:///tmp/lambdas/maintenance_detection.zip \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --environment "Variables={MAINTENANCE_URL=http://maintenance-service:8005}"

awslocal lambda create-event-source-mapping \
  --function-name maintenance-detection-lambda \
  --event-source-arn "$MAINT_QUEUE_ARN"

awslocal lambda create-function \
  --function-name relocation-lambda \
  --runtime python3.11 \
  --handler handler.lambda_handler \
  --zip-file fileb:///tmp/lambdas/relocation.zip \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --environment "Variables={RELOCATION_URL=http://relocation-service:8006}"

awslocal lambda create-event-source-mapping \
  --function-name relocation-lambda \
  --event-source-arn "$RELOC_QUEUE_ARN"