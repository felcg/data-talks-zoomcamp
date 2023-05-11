import os
import pandas as pd
import argparse
from time import time
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    dbName = params.dbName
    tableName = params.tableName
    url = params.url
    parquet_name = "output.parquet"
    csv_name = "output.csv"

    # download the csv
    os.system(f"wget {url} -O {parquet_name}")
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbName}")
    parquet = pd.read_parquet(parquet_name)
    parquet.to_csv(csv_name)
    csv_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(csv_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.head(n=0).to_sql(name=tableName, con=engine, if_exists="replace")
    df.to_sql(name=tableName, con=engine, if_exists="append")

    while True:
        t_start = time()
        df = next(csv_iter)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        df.to_sql(name=tableName, con=engine, if_exists="append")
        t_end = time()
        print("inserted another chunk... took %.3f seconds" % (t_end - t_start))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")

    # user, password, host, port, database name, table name,
    # url of the csv
    parser.add_argument("--user", help="username for postgres")
    parser.add_argument("--password", help="password for postgres")
    parser.add_argument("--host", help="host for postgres")
    parser.add_argument("--port", help="port for postgres")
    parser.add_argument("--dbName", help="database name for postgres")
    parser.add_argument(
        "--tableName", help="name of the table where we will write the results to"
    )
    parser.add_argument("--url", help="url of the csv file")

    args = parser.parse_args()

    main(args)
