import pytest
from sample import get_scheduled_action_of_next_running_instance

# Find the Scheduled actions of given ASG which is going to run next 
# and calcalate elapsed in hh:mm:ss from current time.
def test_get_scheduled_action_of_next_running_instance():
    instance_data = [
        {"InstanceId":"i-1"},
        {"InstanceId":"i-2"}
    ]
    scheduled_actions = [
        {"StartTime":"2023-08-05T12:00:00z","InstanceId":"i-1", "ScheduledActionName":"Action1"},
        {"StartTime":"2023-08-09T12:00:00z","InstanceId":"i-2", "ScheduledActionName":"Action2"}
    ]
    next_instance = instance_data[0]
    next_action = get_scheduled_action_of_next_running_instance(next_instance)
    expected = "Action1"
    assert next_action==expected
