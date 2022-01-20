#!/bin/bash

echo "Building image"
docker build -t 670211327818.dkr.ecr.eu-central-1.amazonaws.com/icecompass:latest .

echo "Logging in to ECR"
aws ecr get-login-password --profile eks | docker login --username AWS --password-stdin 670211327818.dkr.ecr.eu-central-1.amazonaws.com/icecompass

echo "Push to ECR"
docker push 670211327818.dkr.ecr.eu-central-1.amazonaws.com/icecompass:latest
