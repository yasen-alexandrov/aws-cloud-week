## add comment to trigger flow !!!

import json
import pulumi_aws as aws

repo = aws.ecr.Repository("repo",
    name="app_repo",
    image_tag_mutability="MUTABLE",
    image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
        scan_on_push=True,
    ))

vpc = aws.ec2.Vpc("vpc",
    cidr_block="10.0.0.0/16",
    instance_tenancy="default",
    enable_dns_hostnames=True)

sn1 = aws.ec2.Subnet("sn1",
    cidr_block="10.0.1.0/24",
    vpc_id=vpc.id,
    availability_zone="eu-west-1a",
    map_public_ip_on_launch=True)

sn2 = aws.ec2.Subnet("sn2",
    cidr_block="10.0.2.0/24",
    vpc_id=vpc.id,
    availability_zone="eu-west-1b",
    map_public_ip_on_launch=True)

sn3 = aws.ec2.Subnet("sn3",
    cidr_block="10.0.3.0/24",
    vpc_id=vpc.id,
    availability_zone="eu-west-1c",
    map_public_ip_on_launch=True)

sg = aws.ec2.SecurityGroup("sg",
    name="sg",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="https",
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            description="http",
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
    )])

gw = aws.ec2.InternetGateway("gw", vpc_id=vpc.id)

rt = aws.ec2.RouteTable("rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=gw.id,
        ),
        aws.ec2.RouteTableRouteArgs(
            ipv6_cidr_block="::/0",
            gateway_id=gw.id,
        ),
    ])

route1 = aws.ec2.RouteTableAssociation("route1",
    route_table_id=rt.id,
    subnet_id=sn1.id)

route2 = aws.ec2.RouteTableAssociation("route2",
    route_table_id=rt.id,
    subnet_id=sn2.id)

route3 = aws.ec2.RouteTableAssociation("route3",
    route_table_id=rt.id,
    subnet_id=sn3.id)

ecs = aws.ecs.Cluster("ecs", name="app_cluster")

td = aws.ecs.TaskDefinition("td",
    container_definitions=json.dumps([{
        "name": "app",
        "image": "182949046443.dkr.ecr.us-east-2.amazonaws.com/app_repo",
        "cpu": 256,
        "memory": 512,
        "essential": True,
        "portMappings": [{
            "containerPort": 80,
            "hostPort": 80,
        }],
    }]),
    family="app",
    requires_compatibilities=["FARGATE"],
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    task_role_arn="arn:aws:iam::182949046443:role/ecsTaskExecutionRole",
    execution_role_arn="arn:aws:iam::182949046443:role/ecsTaskExecutionRole")

service = aws.ecs.Service("service",
    name="app_service",
    cluster=ecs.arn,
    launch_type="FARGATE",
    enable_execute_command=True,
    deployment_maximum_percent=200,
    deployment_minimum_healthy_percent=100,
    desired_count=1,
    task_definition=td.arn,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        assign_public_ip=True,
        security_groups=[sg.id],
        subnets=[
            sn1.id,
            sn2.id,
            sn3.id,
        ],
    ))


