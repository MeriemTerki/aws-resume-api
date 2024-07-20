import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    # Retrieve the item ID from the event
    item_id = event.get('id', '1')  # Default to '1' if no ID is provided

    try:
        # Fetch item from DynamoDB
        response = dynamodb.get_item(
            TableName='Resumes',
            Key={'id': {'S': item_id}}
        )

        # Check if the item exists
        if 'Item' in response:
            # Convert DynamoDB item to Python dict
            item = response['Item']
            resume_data = item.get('resume', {})

            # Debugging: Print the retrieved data
            print(f"Retrieved data: {resume_data}")

            # Convert from DynamoDB format to JSON format
            json_data = convert_dynamodb_item(resume_data)

            # Reconstruct the ordered data
            ordered_data = reconstruct_order(json_data)

            return {
                'statusCode': 200,
                'body': json.dumps(ordered_data, indent=2),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Item not found'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

def convert_dynamodb_item(item):
    """Convert DynamoDB item format to JSON format."""
    if 'M' in item:
        return {k: convert_dynamodb_item(v) for k, v in item['M'].items()}
    elif 'L' in item:
        return [convert_dynamodb_item(i) for i in item['L']]
    elif 'S' in item:
        return item['S']
    elif 'N' in item:
        return float(item['N'])
    elif 'BOOL' in item:
        return item['BOOL']
    elif 'NULL' in item:
        return None
    else:
        return item

def reconstruct_order(data):
    """Reconstruct data in the desired order."""
    ordered_data = {
        'basics': {
            'name': data.get('basics', {}).get('name', ''),
            'label': data.get('basics', {}).get('label', ''),
            'email': data.get('basics', {}).get('email', ''),
            'phone': data.get('basics', {}).get('phone', ''),
            'summary': data.get('basics', {}).get('summary', ''),
            'location': {
                'address': data.get('basics', {}).get('location', {}).get('address', ''),
                'postalCode': data.get('basics', {}).get('location', {}).get('postalCode', ''),
                'city': data.get('basics', {}).get('location', {}).get('city', ''),
                'countryCode': data.get('basics', {}).get('location', {}).get('countryCode', ''),
                'region': data.get('basics', {}).get('location', {}).get('region', ''),
            },
            'profiles': data.get('basics', {}).get('profiles', [])
        },
        'work': data.get('work', []),
        'education': data.get('education', []),
        'certifications': data.get('certifications', []),
        'skills': data.get('skills', [])
    }
    return ordered_data
