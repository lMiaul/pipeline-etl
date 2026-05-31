import psycopg2
from psycopg2.extras import execute_values
import numpy as np

# Registrar el tipo numpy.int64 para que psycopg2 lo entienda nativamente
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
register_adapter(np.float64, AsIs)

def get_db_connection():
    # Usamos 127.0.0.1 en vez de localhost para evitar problemas de resolución en Windows
    # Usamos puerto 5433 porque el 5432 estaba ocupado por otra instalación local
    return psycopg2.connect(
        host="127.0.0.1",
        port="5433",
        dbname="hr_analytics",
        user="data_engineer",
        password="supersecret"
    )

def create_table_if_not_exists(conn):
    with conn.cursor() as cur:
        # Definimos la tabla. employee_id será la Primary Key.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hr_employees (
                employee_id INTEGER PRIMARY KEY,
                department VARCHAR(255),
                region VARCHAR(255),
                education VARCHAR(255),
                gender VARCHAR(50),
                recruitment_channel VARCHAR(255),
                no_of_trainings INTEGER,
                age INTEGER,
                previous_year_rating FLOAT,
                length_of_service INTEGER,
                kpis_met_gt_80 INTEGER,
                awards_won INTEGER,
                avg_training_score FLOAT,
                is_promoted INTEGER
            );
        """)
    conn.commit()

def load_data_idempotent(df):
    """
    Carga el DataFrame en PostgreSQL usando un UPSERT (Carga Idempotente).
    """
    conn = get_db_connection()
    create_table_if_not_exists(conn)
    
    # Preparamos la query de UPSERT
    # ON CONFLICT (employee_id): Si intentamos insertar un ID que ya existe, no falla, lo actualiza.
    insert_query = """
        INSERT INTO hr_employees (
            employee_id, department, region, education, gender, recruitment_channel, 
            no_of_trainings, age, previous_year_rating, length_of_service, 
            kpis_met_gt_80, awards_won, avg_training_score, is_promoted
        ) VALUES %s
        ON CONFLICT (employee_id) DO UPDATE SET
            department = EXCLUDED.department,
            region = EXCLUDED.region,
            education = EXCLUDED.education,
            gender = EXCLUDED.gender,
            recruitment_channel = EXCLUDED.recruitment_channel,
            no_of_trainings = EXCLUDED.no_of_trainings,
            age = EXCLUDED.age,
            previous_year_rating = EXCLUDED.previous_year_rating,
            length_of_service = EXCLUDED.length_of_service,
            kpis_met_gt_80 = EXCLUDED.kpis_met_gt_80,
            awards_won = EXCLUDED.awards_won,
            avg_training_score = EXCLUDED.avg_training_score,
            is_promoted = EXCLUDED.is_promoted;
    """
    
    # Convertimos el DataFrame a una lista de tuplas para inyectarlo masivamente
    data_tuples = [tuple(x) for x in df.to_numpy()]
    
    with conn.cursor() as cur:
        # execute_values es súper eficiente para cargar miles de filas de golpe
        execute_values(cur, insert_query, data_tuples)
    
    conn.commit()
    conn.close()
    print(f"Cargados/Actualizados {len(df)} registros exitosamente en PostgreSQL.")
