# Data Pipeline ETL: AWS S3 & Lambda Local Emulator

## Descripción
Este proyecto es un pipeline ETL (Extract, Transform, Load) que simula un entorno de AWS de manera local utilizando Docker, Floci (LocalStack) y PostgreSQL. Procesa datos de Recursos Humanos (HR Analytics) extrayendo un archivo CSV desde un bucket S3 simulado, transformando los datos a través de una función Lambda (usando Pandas) y cargándolos en una base de datos PostgreSQL de forma idempotente.

## Arquitectura
- **Amazon S3 (Floci / LocalStack)**: Actúa como el Data Lake donde se almacenan los datos crudos (`hr_data.csv`).
- **AWS Lambda**: Función en Python que se encarga de extraer los datos desde S3, limpiarlos y transformarlos.
- **PostgreSQL**: Base de datos destino que simula un Amazon RDS, donde se guardan los datos ya estructurados.

## Estructura del Proyecto
- `docker-compose.yml`: Configuración de los contenedores Docker para levantar el entorno local con Floci y PostgreSQL.
- `setup_s3.py`: Script para inicializar y crear el bucket (`hr-data-lake`) en el emulador local de AWS.
- `upload_to_s3.py`: Script para subir el archivo de datos crudos (`hr_data.csv`) al bucket S3 simulado.
- `lambda_function.py`: Código central de la función Lambda que orquesta la descarga, limpieza y transformación de los datos.
- `database.py`: Lógica para gestionar la conexión y cargar los datos de forma masiva e idempotente (Upsert) en la base de datos PostgreSQL.
- `requirements.txt`: Dependencias necesarias del proyecto en Python.

## Requisitos Previos
- Docker y Docker Compose instalados.
- Python 3.8+ instalado.
- Entorno virtual de Python (recomendado).

## Instrucciones de Uso

1. **Levantar la Infraestructura Local**
   Inicia los servicios de Floci (emulador de AWS) y PostgreSQL en segundo plano con Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. **Instalar Dependencias**
   Activa tu entorno virtual de Python e instala los paquetes necesarios:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar el Data Lake**
   Crea el bucket en S3 local ejecutando el script de configuración:
   ```bash
   python setup_s3.py
   ```

4. **Subir los Datos Crudos**
   Sube el archivo CSV al bucket S3 recién creado:
   ```bash
   python upload_to_s3.py
   ```

5. **Ejecutar el Pipeline (Simulación de la Lambda)**
   Ejecuta la función Lambda localmente. Esto simulará el evento que descarga el archivo desde S3, aplica las transformaciones y carga los datos resultantes a PostgreSQL:
   ```bash
   python lambda_function.py
   ```

## Transformaciones de Datos
La función Lambda aplica las siguientes transformaciones para asegurar la calidad de los datos en PostgreSQL:
- Estandarización de nombres de las cabeceras (columnas) al formato `snake_case`.
- Imputación de valores nulos (por ejemplo, en `education` se asigna 'Unknown', en `previous_year_rating` se asigna 0.0).
- Validación y conversión de tipos de datos, asegurando que los campos lógicos/booleanos se interpreten como enteros en la base de datos.
- Carga **idempotente** (Upsert) asegurando que si se procesa el mismo `employee_id`, se actualiza el registro en lugar de generar duplicados o errores.