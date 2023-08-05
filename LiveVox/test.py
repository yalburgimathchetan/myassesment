import pytest
from sample import verify_instance_count, verify_instances_availibility_zones, verify_SG_ImageID_VPCID, get_longest_running_ASG_instance

# Test Case - A
# 1- ASG desire running count should be same as running instances. if mismatch fails
def test_verify_instance_count_mismatch():
    desired_count = 4
    running_count = 3
    result = verify_instance_count(desired_count, running_count)
    assert not result

def test_verify_instance_count_match():
    desired_count = 4
    running_count = 4
    result = verify_instance_count(desired_count, running_count)
    assert result

# 2- if more than 1 instance running on ASG, 
# then ec2 instance should on available and distributed on multiple availibity zone.
def test_verify_instances_availibility_zones_single_zone():
    availabilty_zones = {"ap-south-1"}
    result = verify_instances_availibility_zones(availabilty_zones)
    assert not result

def test_verify_instances_availibility_zones_single_zone():
    availabilty_zones = {"ap-south-1","ap-south-2"}
    result = verify_instances_availibility_zones(availabilty_zones)
    assert result

# 3- SecuirtyGroup, ImageID and VPCID should be same on ASG running instances.
def test_verify_SG_ImageID_VPCID_same():
    instance_data = [
        {"InstanceId": "i-1", "SecurityGroups":["sg-1"], "ImageId": "ami-1", "VpcId": "vpc-1"},
        {"InstanceId": "i-2", "SecurityGroups":["sg-1"], "ImageId": "ami-1", "VpcId": "vpc-1"}
    ]
    result = verify_SG_ImageID_VPCID(instance_data)
    assert result

def test_verify_SG_ImageID_VPCID_mismatch():
    instance_data = [
        {"InstanceId": "i-1", "SecurityGroups":["sg-1"], "ImageId": "ami-1", "VpcId": "vpc-1"},
        {"InstanceId": "i-2", "SecurityGroups":["sg-2"], "ImageId": "ami-2", "VpcId": "vpc-2"}
    ]
    result = verify_SG_ImageID_VPCID(instance_data)
    assert not result

# 4- Findout uptime of ASG running instances and get the longest running instance.
def test_get_longest_running_ASG_instance():
    data = {
        "i-1":"2023-08-05T00:00:00z",
        "i-2":"2023-08-05T00:30:00z"
    }
    longest_instance = get_longest_running_ASG_instance(data)
    expected = {"i-1":"2023-08-05T00:00:00z"}
    assert longest_instance==expected
