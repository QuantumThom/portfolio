from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    core as cdk,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_logs as logs,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_cloudmap as cloudmap,
)

from aws_cdk.aws_stepfunctions import (
    IntegrationPattern,
    JsonPath,
)


from aws_cdk.aws_stepfunctions_tasks import (
    ContainerOverride,
    EcsRunTask,
    TaskEnvironmentVariable,
    EcsFargateLaunchTarget,
)
from constructs import Construct

# test 

class PortfolioStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # fargate task role
        task_role = iam.Role(
            scope=self,
            id="FargateTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess")
            ],
        )
        
        # container logs
        pf_log_group = logs.LogGroup(self, "Log Group", log_group_name="pf_log_group")
        
        pf_log_driver = ecs.LogDriver.aws_logs(
            stream_prefix="pf", log_group=pf_log_group)
        
        
        # Create an ECS cluster
        cluster = ecs.Cluster(self, "FlaskCluster"
        )
        
        # Add capacity to it
        cluster.add_capacity(
            instance_type=ec2.InstanceType("t3a.micro")
        )
        
        task_definition = ecs.Ec2TaskDefinition(self, "FlaskTaskDef")
        
        container = task_definition.add_container(
            "sf_container",
            image=ecs.AssetImage(
                "./resources/flask/src"),
            logging=pf_log_driver,
        )
        
        container.add_port_mappings(
            container_port = 8888,
            host_port = 5000
            )
        
        # Instantiate an Amazon ECS Service
        ecs_service = ecs.Ec2Service(self, "FlaskService",
            cluster=cluster,
            task_definition=task_definition,
            cloud_map_options=ecs.CloudMapOptions(
             # Create SRV records - useful for bridge networking
            dns_record_type=cloudmap.DnsRecordType.SRV,
             # Targets port TCP port 8888 `Container`
            container = container,
            container_port=8888
            )
        )