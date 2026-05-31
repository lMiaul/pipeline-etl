import boto3

def get_s3_client():
    """
    Crea y retorna un cliente de S3 configurado para apuntar a nuestro emulador local (Floci).
    """
    # En un entorno real, boto3 lee las credenciales ocultas en tu sistema.
    # Como estamos en local, forzamos estas variables.
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',      # Credenciales falsas obligatorias
        aws_secret_access_key='test',  # Credenciales falsas obligatorias
        region_name='us-east-1'
    )

def setup_bucket(bucket_name):
    s3 = get_s3_client()
    
    print(f"Intentando crear el bucket: {bucket_name}...")
    s3.create_bucket(Bucket=bucket_name)
    
    # Listamos los buckets para confirmar
    response = s3.list_buckets()
    print("\nBuckets actuales en tu Floci local:")
    for bucket in response.get('Buckets', []):
        print(f" - {bucket['Name']}")

if __name__ == "__main__":
    setup_bucket('hr-data-lake')
