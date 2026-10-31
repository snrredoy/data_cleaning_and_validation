
import pandas as pd
import psycopg

DB_NAME = "data_cleaning_db"


def get_connection():
    return psycopg.connect(dbname=DB_NAME)


def test_connection():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT current_user, current_database();"
            )
            result = cur.fetchone()

    return result


def insert_customers(
    df: pd.DataFrame,
    batch_size: int = 500,
) -> int:
    if batch_size < 1:
        raise ValueError("batch_size must be greater than zero")

    required_columns = ["customer_id", "name", "email", "city"]

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    records = df[required_columns].astype(object).where(
        pd.notna(df[required_columns]), None
    )

    rows = list(records.itertuples(index=False, name=None))

    result = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
    }

    if not rows:
        return result


    query = """
        INSERT INTO customers (customer_id, name, email, city)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (customer_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            city = EXCLUDED.city,
            updated_at = NOW()
        WHERE 
            (customers.name, customers.email, customers.city) IS DISTINCT FROM
            (EXCLUDED.name, EXCLUDED.email, EXCLUDED.city)
        RETURNING (xmax=0) AS is_inserted;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            for start in range(0, len(rows), batch_size):
                batch = rows[start:start + batch_size]

                for row in batch:
                    cur.execute(query, row)

                    returned_rows = cur.fetchone()

                    if returned_rows is None:
                        result["unchanged"] += 1
                    elif returned_rows[0]:
                        result["inserted"] += 1
                    else:
                        result["updated"] += 1

    return result

if __name__ == "__main__":
    print("Database connection successful!")
    print("Connected user and database:", test_connection())
