import * as awsx from '@pulumi/awsx';
import * as aws from '@pulumi/aws';
import * as pulumi from '@pulumi/pulumi';
import { dnsName } from './config';

export const createWebserverContainer = (webServerImage: pulumi.Input<string>, listener: awsx.elasticloadbalancingv2.ApplicationListener): awsx.ecs.Container => {
    return {
        image: webServerImage,
        essential: true,
        portMappings: [
            listener
        ]
    }
}

export const createApplicationServerContainer = (appServerImage: pulumi.Input<string>, redis: aws.elasticache.Cluster, entryPoint?: string[]): awsx.ecs.Container => {
    return {
        image: appServerImage,
        essential: true,
        entryPoint: entryPoint,
        secrets: [
            {
                name: "RDS_USERNAME",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass-api-OnVp2S:username::"
            },
            {
                name: "RDS_PASSWORD",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass-api-OnVp2S:password::"
            },
            {
                name: "RDS_HOSTNAME",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass-api-OnVp2S:host::"
            },
            {
                name: "RDS_DB_NAME",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass-api-OnVp2S:dbname::"
            },
            {
                name: "ICETEST_RABBIT_HOST",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icetest/rabbitmq-GNFrDL:host::",
            },
            {
                name: "ICETEST_RABBIT_PASSWORD",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icetest/rabbitmq-GNFrDL:password::",
            },
            {
                name: "ICETEST_RABBIT_USER",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icetest/rabbitmq-GNFrDL:username::",
            },
            {
                name: "ICETEST_RABBIT_VHOST",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icetest/rabbitmq-GNFrDL:vhost::",
            },
            {
                name: "MAIL_PASSWORD",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass/smtp-QOWzOg:password::",
            },
            {
                name: "MAIL_PORT",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass/smtp-QOWzOg:port::",
            },
            {
                name: "MAIL_SERVER",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass/smtp-QOWzOg:server::",
            },
            {
                name: "MAIL_USERNAME",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass/smtp-QOWzOg:username::",
            },
            {
                name: "SENTRY_DSN",
                valueFrom: "arn:aws:secretsmanager:eu-central-1:670211327818:secret:prod/icecompass/sentry-ej0dya:dsn::",
            }
        ],
        environment: [
            {
                name: "REDIS_URL",
                value: pulumi.interpolate`redis://${redis.cacheNodes[0].address}:${redis.cacheNodes[0].port}/0`,
            },
            {
                name: "SECRET_KEY",
                value: (Math.random() + 1).toString(36).substring(50),
            },
            {
                name: "SERVER_NAME",
                value: dnsName
            }
            
        ]
    }
}