import * as awsx from '@pulumi/awsx';
import { certificateArn } from './config';

export const createLoadbalancer = (vpc: awsx.ec2.Vpc): [awsx.lb.ApplicationLoadBalancer, awsx.lb.TargetGroup ,awsx.elasticloadbalancingv2.ApplicationListener] => {
    const lb = new awsx.lb.ApplicationLoadBalancer("nginx-lb", { vpc });

    const targetGroup = lb.createTargetGroup('lb-target', {
        port: 80,
        targetType: "ip",
        // stickiness: {
        //     enabled: true,
        //     type: "lb_cookie",
        //     cookieDuration: 604800
        // }
    });

    const http = lb.createListener("http-listener", {
        protocol: "HTTP",
        targetGroup,
    });

    const https = lb.createListener("https-listener", {
        protocol: "HTTPS",
        certificateArn: certificateArn,
        targetGroup
    });

    return [lb, targetGroup, https];
}