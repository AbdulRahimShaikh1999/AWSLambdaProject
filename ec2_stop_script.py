import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Extract query parameters from API Gateway request
    params = event.get("queryStringParameters") or {}
    tag_key = params.get("key")
    tag_value = params.get("value")

    if not tag_key or not tag_value:
        return {
            "statusCode": 400,
            "body": "Missing required query parameters: 'key' and 'value'"
        }

    # Build EC2 tag filter
    filters = [
        {'Name': 'instance-state-name', 'Values': ['running']},
        {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
    ]

    try:
        # Describe matching instances
        response = ec2.describe_instances(Filters=filters)
        instances_to_stop = [
            instance["InstanceId"]
            for reservation in response["Reservations"]
            for instance in reservation["Instances"]
        ]

        if instances_to_stop:
            ec2.stop_instances(InstanceIds=instances_to_stop)
            result = f"Stopped instances: {instances_to_stop}"
        else:
            result = "No matching instances found."

        return {
            "statusCode": 200,
            "body": result
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Internal error: {str(e)}"
        }
