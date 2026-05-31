import pandas as pd
import io
import boto3
from database import load_data_idempotent
import traceback

def clean_hr_data(csv_content):
    """
    Función pura (sin efectos secundarios) para limpiar y transformar los datos de RRHH.
    Esta será la lógica principal o "corazón" de nuestra AWS Lambda.
    """
    # 1. Leer el CSV desde texto crudo (en la vida real vendrá del evento de S3)
    df = pd.read_csv(io.StringIO(csv_content))
    
    # 2. Estandarización de cabeceras a snake_case
    # Esto es crucial para evitar dolores de cabeza con comillas dobles y mayúsculas en PostgreSQL.
    df.columns = df.columns.str.lower()                  # Todo a minúsculas
    df.columns = df.columns.str.replace(' ', '_')        # Espacios por guiones bajos
    df.columns = df.columns.str.replace('?', '')         # Quitar signos de interrogación
    df.columns = df.columns.str.replace('>80%', 'gt_80') # Renombrar caracteres especiales

    # 3. Manejo de Calidad de Datos (Nulos)
    # Educación: si un empleado no llenó este campo, asumimos 'Unknown'
    if 'education' in df.columns:
        df['education'] = df['education'].fillna('Unknown')
    
    # Calificación previa: si es nulo, probablemente sea su primer año. Lo imputamos con 0.
    if 'previous_year_rating' in df.columns:
        df['previous_year_rating'] = df['previous_year_rating'].fillna(0.0)

    # 4. Validación de tipos (Variables binarias a Enteros)
    # Algunos sistemas envían booleanos o flotantes, los forzamos a enteros 0 o 1
    for col in ['is_promoted', 'awards_won']:
        if col in df.columns:
            # fillna(0) por si hay un nulo extraño antes de convertir a entero
            df[col] = df[col].fillna(0).astype(int)
            
    return df



def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )

if __name__ == "__main__":
    print("----- SIMULANDO EVENTO DE S3 Y EJECUTANDO LAMBDA -----")
    
    try:
        # 1. Nos conectamos a S3 (nuestro Data Lake)
        s3 = get_s3_client()
        bucket = 'hr-data-lake'
        key = 'hr_data.csv'
        
        print(f"Descargando archivo {key} desde el bucket {bucket}...")
        response = s3.get_object(Bucket=bucket, Key=key)
        
        # Leemos el contenido directamente de la memoria sin guardarlo en disco
        csv_content = response['Body'].read().decode('utf-8')
        
        # 2. Ejecutamos la transformación
        print("Limpiando y transformando datos...")
        df_limpio = clean_hr_data(csv_content)
        
        # 3. Cargamos los datos limpios en la Base de Datos (PostgreSQL)
        print("Iniciando carga idempotente en PostgreSQL...")
        load_data_idempotent(df_limpio)
        
    except Exception as e:
        
        print(f"Error al ejecutar el flujo:")
        traceback.print_exc()
