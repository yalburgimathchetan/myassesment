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
    running_instance_count = get_running_instance_count(asginfo)
    if running_instance_count <= 0:
        print("There are no running ASG instances")
    else:
        for asg in asginfo["AutoScalingGroups"]:
            for asg_instance in asg["Instances"]:
                asg_insatnce_ids.append(asg_instance["InstanceId"])
    return asg_insatnce_ids

def get_ec2_instance():
    ec2 = boto3.client("ec2", aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    return ec2

def get_ec2_instance_ids():
    ec2 = get_ec2_instance()
    ec2_info = ec2.describe_instances()
    # print(ec2_info)
    instance_ids = []
    for reservation in ec2_info["Reservations"]:
        for instance in reservation["Instances"]:
            instance_ids.append(instance["InstanceId"])
    return instance_ids

def get_ec2_instance_info():
    """
    This function returns ec2_instnace_info_dict
    {"Id":[state, availibility_zone, launch_time, SecuirtyGroup, ImageID, VPCID, ]}
    """
    ec2 = get_ec2_instance()
    ec2_info = ec2.describe_instances()
    ec2_instance_info_dict=dict()
    for reservation in ec2_info["Reservations"]:
        for instance in reservation["Instances"]:
            ec2_inst_id = instance["InstanceId"]
            ec2_inst_state = instance["State"]["Name"]
            ec2_inst_avail_zone = instance["Placement"]["AvailabilityZone"]
            ec2_inst_launch_time = instance["LaunchTime"]
            ec2_inst_sec_group_id = instance["SecurityGroups"][0]["GroupId"]
            ec2_inst_imageid = instance["ImageId"]
            ec2_inst_vpcid = instance["VpcId"]
            ec2_instance_info_dict.update({ec2_inst_id:[
                ec2_inst_state, ec2_inst_avail_zone, ec2_inst_launch_time, ec2_inst_sec_group_id,
                ec2_inst_imageid, ec2_inst_vpcid
            ]})
    return ec2_instance_info_dict

def get_ec2_instance_state(ec2_instance_id):
    if ec2_instance_id is not None:
        ec2 = get_ec2_instance()
        instance_info = ec2.describe_instances(InstanceIds=[ec2_instance_id])
        instance_state = instance_info["Reservations"][0]["Instances"][0]["State"]["Name"]
        print("Status of Instance id {} is: {} ".format(ec2_instance_id, instance_state))
        return instance_state
    else:
        print("Please pass correct instance id as arguments to get instance state")

def verify_instances_availibility_zones():
    status = False
    zones = set()
    states = set()
    ec2_inst_info = get_ec2_instance_info()    
    if len(ec2_inst_info) >1:
        for key,value in ec2_inst_info.items():
            zones.add(value[1])
            states.add(value[0])
        if len(zones) == len(ec2_inst_info.keys()):
            print("Instnaces are distributed on multiple availibity zone.")
            status = True
    else:
        print("More than 1 instances are not running on ASG")
    return status
   
def check_ASG_instance_has_same_securitygroup_image_vpc(asginfo):
    status = False
    asg_insatnce_ids = get_asg_instance_ids(asginfo)
    ec2 = get_ec2_instance()
    ec2_infos = ec2.describe_instances(InstanceIds=asg_insatnce_ids)
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    launchTempID = asginfo["AutoScalingGroups"][0]["LaunchTemplate"]["LaunchTemplateId"]
    
    launch_config = ec2.describe_launch_templates(LaunchTemplateIds=[launchTempID])["LaunchConfigurations"][0]
    first_instance_sg = launch_config["SecurityGroups"][0]["GroupId"]
    first_instance_image_id =launch_config["ImageId"]
    first_instance_vpcid = ec2_infos["ClassicLinkVPCId"]

    all_same = all(
        instance["SecurityGroups"][0]["GroupId"]==first_instance_sg and 
        instance["ImageId"]==first_instance_image_id and 
        instance["VpcId"]==first_instance_vpcid 
        for reservation in ec2_infos["Reservations"]
        for instance in reservation["Instances"]
    )
    if all_same:
        status = True
    return status

def verify_SG_ImageID_VPCID():
    pass
    
def get_uptime_and_longest_running_ASG_instances(asginfo):
    asg_insatnce_ids =[]
    asg_instance_ids = get_asg_instance_ids(asginfo)
    if len(asg_insatnce_ids) < 1 :
        print("There are no running ASG instances")
        return None
    ec2 = get_ec2_instance() 
    ec2_info = ec2.describe_instances(InstanceId=asg_insatnce_ids)
    asg_instance_uptime_dict = dict()
    for reservation in ec2_info["Reservations"]:
        for instance in reservation["Instances"]:
            launch_time = instance["LunchTime"]
            current_time = datetime.datetime.now(datetime.timezone.utc)
            uptime = current_time - launch_time
            asg_instance_uptime_dict.update({instance:uptime})
            print("ASG instance {} is up for:  {}".format(instance,uptime))
    get_longest_running_ASG_instance(asg_instance_uptime_dict)
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
        # print(action)
        if action["StartTime"] > current_time:
            next_action = action["ScheduledActionName"]
            break
    if next_action is None:
        print("No ASG instance is scheduled to run")
    else:
        print("Scheduled actions of given ASG which is going to run next is {}".format(next_action))
    return next_action

def get_launch_and_term_count(asgname):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    resp = asg_client.describe_scaling_activities(AutoScalingGroupName=asgname)
    # print(resp)
    launch_count = 0
    term_count = 0
    date_format = "%Y-%m-%d %H:%M:%S"
    current_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
    print()
    start = current_time.replace(hour=0, minute=0, second=0, microsecond=000000)
    end = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    # print(current_time)
    # print(start)
    # print(end)
    for activity in resp["Activities"]:
        activity_time = activity["StartTime"]
        # activity_time = datetime.datetime.strptime(str(activity_time), date_format)
        print(activity_time)

        if start <= activity_time <= end:
            if activity["StatusCode"] == "Successful" and activity["Cause"].startswith("At 2023"):
                launch_count += 1
            elif activity["StatusCode"] == "Successful" and activity["Cause"].startswith("Terminating instance"):
                term_count += 1
        break
    print("The total number of instances lunched are {} ".format(launch_count))
    print("The total number of instnaces terminated today are {}".format(term_count))
    print("For The given ASG name is {}".format(asgname))

def main(argv):
    print(sys.argv)
    if len(sys.argv)>1:
        asgname = str(sys.argv[1])
        response=get_asg_describe(asgname)
        # print(response)
        ## Test Case - A
        ## 1- ASG desire running count should be same as running instances. if mismatch fails
        desired_count = get_desired_count(response)
        running_count = get_running_instance_count(response)
        verify_instance_count(desired_count, running_count)
        
        ## 2- if more than 1 instance running on ASG, 
        ## then ec2 instance should on available and distributed on multiple availibity zone.
        # get_asg_instance_ids(response)
        # ec2_inst_info = get_ec2_instance_info()
        # print(ec2_inst_info)
        print(verify_instances_availibility_zones())

        ## 3- SecuirtyGroup, ImageID and VPCID should be same on ASG running instances.
        # check_ASG_instance_has_same_securitygroup_image_vpc(response)

        ## 4- Findout uptime of ASG running instances and get the longest running instance.
        get_uptime_and_longest_running_ASG_instances(response)

        ## Testcase:- B
        ## Find the Scheduled actions of given ASG which is going to run next 
        ## and calcalate elapsed in hh:mm:ss from current time.
        get_scheduled_action_of_next_running_instance(asgname)

        ## Calculate total number instances lunched and terminated on current day for the given ASG.
        get_launch_and_term_count(asgname)
        

    else:
        print("Please pass correct arguments")
        print("Usage ./sample-test.py asgname")


if __name__ == "__main__":
    main(sys.argv)
