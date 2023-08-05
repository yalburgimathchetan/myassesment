import sample

def validate_asg_instance(desired_count, running_instance_count):
    assert desired_count != running_instance_count, "ASG desire running count is not same as running instances"

def check_instance_state(instance_ids):
    for instance_id in instance_ids:
        instance_state = sample.get_instance_state(instance_id)
        assert instance_state != "running", "Instance Id {} is not running".format(instance_id)

def check_instance_is_distributed_to_multiple_zone(availabilty_zones):
    assert len(availabilty_zones)<=1 , "ec2 instances are not ditributed to mutilple zones"

def validate_ASG_instance_has_same_securitygroup_image_vpc(asginfo):
    assert check_ASG_instance_has_same_securitygroup_image_vpc(asginfo) != True, "Instances have different SG ID, Image ID and VPCID"
