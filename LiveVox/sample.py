import boto3
import os
import sys
import datetime


aws_access_key_id=os.environ['aws_access_key_id']
aws_secret_access_key=os.environ['aws_secret_access_key']


def get_asg_describe(asgname):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asgname])
    return asg_response

def get_desired_count(asginfo):
    if asginfo is not None:
        desired_count = asginfo["AutoScalingGroups"][0]["DesiredCapacity"]
        print("The desired count for given ASG is {}".format(desired_count))
        return desired_count
    else:
        print("Please pass correct ASG info as arguments to get desired count")

def get_running_instance_count(asginfo):
    if asginfo is not None:
        running_instance_list = asginfo["AutoScalingGroups"][0]["Instances"]
        running_instance_count = len(running_instance_list)
        print("The running instance count for given ASG is {}".format(running_instance_count))
        return running_instance_count
    else:
        print("Please pass correct ASG info as arguments to get running instance count")

def verify_instance_count(desired_count, running_count):
    status = False
    if desired_count == running_count:
        status = True
    return status

def get_asg_instance_ids(asginfo):
    asg_insatnce_ids = []
    for asg in asginfo["AutoScalingGroups"]:
        for asg_instance in asg["Instances"]
            asg_insatnce_ids.append(asg_instance["InstanceId"])
    return asg_insatnce_ids

def get_instance_ids()
    ec2 = boto3.client("ec2")
    ec2_info = ec2.describe_instances()
    instance_ids = []
    for reservation in ec2_info["Reservations"]:
        for instance in reservation["Instances"]
            instance_ids.append(instance)
    return instance_ids

def get_instance_state(instance_id):
    if instance_id is not None:
        ec2 = boto3.client("ec2")
        instance_info = ec2.describe_instances(InstanceIds=[instance_id])
        instance_state = instance_info["Reservations"][0]["Instances"][0]["State"]["Name"]
        print("Status of Instance id {} is: {} ".format(instance_id, instance_state))
        return instance_state
    else:
        print("Please pass correct instance id as arguments to get instance state")

def get_instances_availibility_zones():
    ec2 = boto3.client("ec2")
    ec2_info = ec2.describe_instances()
    availabilty_zones = set()
    for reservation in ec2_info["Reservations"]:
        for instance in reservation["Instances"]:
            availabilty_zone = instance["Placement"]["AvailabilityZone"]
            availabilty_zones.add(availabilty_zone)
    return availabilty_zones

def verify_instances_availibility_zones():
    status = False
    availabilty_zones = get_instances_availibility_zones()
    if len(availabilty_zones)>1:
        status = True
    return status
    
def check_ASG_instance_has_same_securitygroup_image_vpc(asginfo):
    status = False
    asg_insatnce_ids = get_asg_instance_ids(asginfo)
    ec2 = boto3.client("ec2")
    ec2_infos = ec2.describe_instances(InstanceIds=asg_insatnce_ids)

    first_instance_sg = ec2_infos["Reservations"][0]["Instances"][0]["SecurityGroups"][0]["GroupId"]
    first_instance_image_id = ec2_infos["Reservations"][0]["Instances"][0]["ImageId"]
    first_instance_vpcid = ec2_infos["Reservations"][0]["Instances"][0]["VpcId"]

    all_same = all(
        instance["SecurityGroups"][0]["GroupId"]==first_instance_sg and 
        instance["ImageId"]==first_instance_image_id and 
        instance["VpcId"]==first_instance_vpcid )
        for reservation in ec2_infos["Reservations"]
        for instance in reservation["Instances"]
    )
    if all_same:
        status = True
    return status

def verify_SG_ImageID_VPCID():
    pass
    
def get_uptime_of_running_ASG_instances(asginfo):
    asg_instance_ids = get_asg_instance_ids(asginfo)
    ec2 = boto3.client("ec2")
    ec2_info = ec2.describe_instances(InstanceId=asg_insatnce_ids)
    asg_instance_uptime_dict = dict()
    for reservation in ec2_info["Reservations"]:
        for instance in reservation["Instances"]:
            launch_time = instance["LunchTime"]
            current_time = datetime.datetime.now(datetime.timezone.utc)
            uptime = current_time - launch_time
            asg_instance_uptime_dict.update({instance:uptime})
            print("ASG instance {} is up for:  {}".format(instance,uptime))
    return asg_instance_uptime_dict

def get_longest_running_ASG_instance(asg_instance_uptime_dict):
    max_uptime = max(asg_instance_uptime_dict.values())
    keys_with_max_uptime = [key for key, value in asg_instance_uptime_dict.items() if value==max_uptime]

    for key in keys_with_max_uptime:
        print("{} instnace has maximum running uptime for: {}".format(key,asg_instance_uptime_dict[key]))

def get_scheduled_action_of_next_running_instance(asgname):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    asg_response = asg_client.describe_scheduled_actions(AutoScalingGroupName=asgname)
    
    current_time = datetime.datetime.now(datetime.timezone.utc)
    next_action = None
    for action in asg_response["ScheduledUpdateGroupActions"]:
        if action["StartTime"] > current_time:
            next_action = action["ScheduledActionName"]
            break
    return next_action

def get_instance_launch_time_dict(asgname):
    ec2 = boto3.client("ec2")
    asg_info = ec2.describe_instances(Filters=[{"Name":"tag:aws:autoscaling:groupName", "Values":[asgname]}])
    instance_launch_time_dict = dict()
    for reservation in asg_info["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            launch_time = instance["LaunchTime"]
            instance_launch_time_dict.update({instance_id:launch_time})

def main(argv):
    print(sys.argv)
    if len(sys.argv)>1:
        response=get_asg_describe(str(sys.argv[1]))
        print(response)
        desired_count = get_desired_count(response)
        running_count = get_running_instance_count(response)
    else:
        print("Please pass correct arguments")
        print("Usage ./sample-test.py asgname")


if __name__ == "__main__":
    main(sys.argv)
