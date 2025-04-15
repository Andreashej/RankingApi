import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

export const createRedisCluster = (vpc: awsx.ec2.Vpc, securityGroup: aws.ec2.SecurityGroup) => {
    const subnetGroup = new aws.elasticache.SubnetGroup('redis-group', {
        subnetIds: vpc.privateSubnetIds
    });

    return new aws.elasticache.Cluster("icecompass-redis", {
        subnetGroupName: subnetGroup.name,
        engine: "redis",
        engineVersion: "6.2",
        nodeType: "cache.t2.micro",
        numCacheNodes: 1,
        port: 6379,
        securityGroupIds: [securityGroup.id]
   });
}