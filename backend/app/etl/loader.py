import pandas as pd
from app.core.logger import etl_logger
from app.database.mongodb import save_cleaned_data
from app.database.mysql_db import engine
from sqlalchemy import text


def load_to_mongodb(df: pd.DataFrame, job_id: str) -> int:
    records = df.to_dict(orient="records")
    count = save_cleaned_data(records, job_id)
    etl_logger.info(f"Loaded {count} records to MongoDB (job={job_id})")
    return count


def load_to_mysql(df: pd.DataFrame, table_name: str = "etl_data", if_exists: str = "replace") -> int:
    try:
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
        etl_logger.info(f"Loaded {len(df)} rows into MySQL table '{table_name}'")
        return len(df)
    except Exception as e:
        etl_logger.error(f"MySQL load failed: {e}")
        raise


def load_to_csv(df: pd.DataFrame, output_path: str) -> str:
    df.to_csv(output_path, index=False)
    etl_logger.info(f"Saved cleaned data to CSV: {output_path}")
    return output_path
