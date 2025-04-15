import * as pulumi from '@pulumi/pulumi';

const config = new pulumi.Config('icecompass')

export const certificateArn = config.get('certificateArn');
export const hostedZoneId = config.require('hostedZoneId');
export const dnsName = config.require('dnsName');