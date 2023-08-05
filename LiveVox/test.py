import pytest
from sample import verify_instance_count, verify_instances_availibility_zones

#Test Case - A
#1- ASG desire running count should be same as running instances. if mismatch fails
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

#2- if more than 1 instance running on ASG, 
# then ec2 instance should on available and distributed on multiple availibity zone.
def test_verify_instances_availibility_zones_single_zone():
    availabilty_zones = {"ap-south-1"}
    result = verify_instances_availibility_zones(availabilty_zones)
    assert not result

def test_verify_instances_availibility_zones_single_zone():
    availabilty_zones = {"ap-south-1","ap-south-2"}
    result = verify_instances_availibility_zones(availabilty_zones)
    assert result

