import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";
import { createRedisCluster } from "./lib/redis";
import { createWebserverContainer, createApplicationServerContainer } from "./lib/application";
import { createLoadbalancer } from './lib/loadbalancer';
import { dnsName, hostedZoneId } from "./lib/config";

const appRepo = new awsx.ecr.Repository("icecompass-api");

const appServerImage = appRepo.buildAndPushImage("../");

const webserverRepo = new awsx.ecr.Repository("icecompass-nginx");

const webServerImage = webserverRepo.buildAndPushImage("../nginx");

const vpc = new awsx.ec2.Vpc('icecompass-vpc', {
    numberOfAvailabilityZones: 2,
})

const cluster = new awsx.ecs.Cluster("icecompass-cluster", { vpc });

const redis = createRedisCluster(vpc, cluster.securityGroups[0].securityGroup);

const [loadbalancer, targetGroup, listener] = createLoadbalancer(vpc);

const taskExecutionRole = new aws.iam.Role('task-execution-role', {
    assumeRolePolicy: {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "ecs-tasks.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    },
    managedPolicyArns: [
        'arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy',
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    ],
    inlinePolicies: [
        {
            name: "SecretsManagerReadAccess",
            policy: JSON.stringify({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "secretsmanager:GetSecretValue",
                            "kms:Decrypt"
                        ],
                        "Resource": [
                            "arn:aws:secretsmanager:eu-central-1:670211327818:secret:*",
                            "arn:aws:kms:eu-central-1:670211327818:*"
                        ]
                    }
                ]
            }),
        }
    ]
})

const apiService = new awsx.ecs.FargateService("api-service", {
    cluster: cluster,
    desiredCount: 2,
    taskDefinitionArgs: {
        containers: {
            'webserver': createWebserverContainer(webServerImage, listener),
            'appserver': createApplicationServerContainer(appServerImage, redis)
        },
        executionRole: taskExecutionRole
    },
});

const rqWorker = new awsx.ecs.FargateService("rq-worker", {
    cluster: cluster,
    desiredCount: 2,
    taskDefinitionArgs: {
        container: createApplicationServerContainer(appServerImage, redis, ['./rq-worker.sh']),
        executionRole: taskExecutionRole
    },
    
});

const rabbitmqWorker = new awsx.ecs.FargateService("rabbitmq-worker", {
    cluster: cluster,
    desiredCount: 1,
    taskDefinitionArgs: {
        container: createApplicationServerContainer(appServerImage, redis, ['./rabbitmq-listener.sh']),
        executionRole: taskExecutionRole
    },
});

const cronJob = new awsx.ecs.FargateTaskDefinition('cron-job', {
    container: createApplicationServerContainer(appServerImage, redis, ['./recompute-rankings-job.sh'])
})

const dnsRecord = new aws.route53.Record('icecompass-dns-record', {
    zoneId: hostedZoneId,
    name: dnsName,
    type: 'A',
    aliases: [{
        name: loadbalancer.loadBalancer.dnsName,
        zoneId: loadbalancer.loadBalancer.zoneId,
        evaluateTargetHealth: true
    }],
    allowOverwrite: true
});

export const url = loadbalancer.loadBalancer.dnsName;
export const dns = dnsRecord.name;