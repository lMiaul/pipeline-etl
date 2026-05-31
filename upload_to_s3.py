import boto3

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )

def upload_to_s3():
    s3 = get_s3_client()
    bucket_name = 'hr-data-lake'
    file_path = 'hr_data.csv'
    
    print(f"Subiendo {file_path} al bucket {bucket_name} en Floci...")
    s3.upload_file(file_path, bucket_name, file_path)
    print("¡Subida completada con éxito!")

if __name__ == "__main__":
    upload_to_s3()
