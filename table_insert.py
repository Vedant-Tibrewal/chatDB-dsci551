import pandas as pd
import mysql.connector
from pymongo import MongoClient
import sys
import json

from src.chatdb.core.utils import normalize_column_names, infer_mysql_datatype, show_tables_and_primary_keys, generate_dynamic_schema
from src.chatdb.core.io import read_json, write_json


def insert_csv_to_mysql(csv_file, db_config, table_name, db_schema):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    df = normalize_column_names(df)
    # Establish a connection to the MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
    # Create the table
        columns = df.columns.tolist()
        sql_types = {col: infer_mysql_datatype(dtype) for col, dtype in df.dtypes.items()}
        column_definitions = [f"{col} {sql_types[col]}" for col in columns]
        db_schema[table_name] = {}
        db_schema[table_name] = {**sql_types}

        pk_columns = ["Create new auto-increment primary key"] + columns
        
        # Ask user to select primary key
        print("Select the primary key column:")
        for i, col in enumerate(pk_columns):
            print(f"{i}. {col}")
        pk_choice = int(input("Enter the number of the primary key column: "))
        
        db_schema[table_name]["pk"] = []
        if pk_choice == 0:
            column_definitions.insert(0, "id INT AUTO_INCREMENT PRIMARY KEY")
            db_schema[table_name]["pk"].append("id")

        else:
            db_schema[table_name]["pk"].append(columns[pk_choice - 1])
            column_definitions[pk_choice - 1] += " PRIMARY KEY"
        
        # Ask user if they want to add a foreign key
        db_schema[table_name]["fk"] = dict()
        add_fk = input("Do you want to add a foreign key? (y/n): ").lower() == 'y'
        if add_fk:
            fk_num = int(input("how many foreign keys present?"))
            print("select foreign table and its primary key")
            primary_keys = show_tables_and_primary_keys(db_config)
            for i, table in enumerate(primary_keys):
                print(f"{i}. {table}")

            fk_definition = ""

            while fk_num>0:

                fk_choice = int(input("Enter the number of the table and pk associated: "))
                
                fk_table = primary_keys[fk_choice][0]
                fk_ref_column = primary_keys[fk_choice][1]
                db_schema[table_name]["fk"][fk_table] = fk_ref_column
                fk_column = input("Enter the name of the foreign key column in current table: ")
                fk_definition += f", FOREIGN KEY ({fk_column}) REFERENCES {fk_table}({fk_ref_column})"
                fk_num -= 1
        else:
            fk_definition = ""

        print("schema check", db_schema)
        
        # Create table SQL
        create_table_sql = f""" 
        CREATE TABLE {table_name} (
            {', '.join(column_definitions)}
            {fk_definition}
        )
        """
        cursor.execute(create_table_sql)
        print(f"Table {table_name} created successfully.")
    # Insert DataFrame records one by one
    for _, row in df.iterrows():
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(row))

    write_json(db_schema, "src/chatdb/constants/db_schema.json")

    
    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Data inserted into {table_name} successfully.")


def insert_json_to_mongodb(json_file, mongo_uri, db_name, collection_name, db_schema):
    # Read the JSON file into a DataFrame
    df = pd.read_json(json_file)
    
    # Establish a connection to the MongoDB database
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    # Insert records into the collection
    documents = json.loads(df.to_json(orient='records'))
    collection.insert_many(documents)

    db_schema[collection_name] = generate_dynamic_schema(documents)

    print(db_schema)

    write_json(db_schema, "src/chatdb/constants/db_schema.json")
    
    # Close the connection
    client.close()


# Main execution
if __name__ == '__main__':

    conn_string = "mongodb://localhost:27017/"
    db_name = "chatdb"
    coll_name = "patients"
    mysql_configs = read_json("src/chatdb/constants/config.json")
    db_schema = read_json("src/chatdb/constants/db_schema.json")

    if len(sys.argv) < 2:
        print("Usage: python table_insert.py [operation] [arguments]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'load_sql':
        if len(sys.argv) < 3:
            print("Usage: python table_insert.py load_sql <csv_file> <table_name>")
            sys.exit(1)
        csv_file = sys.argv[2]
        table_name = sys.argv[3]
        insert_csv_to_mysql(csv_file, mysql_configs, table_name, db_schema)
    
    elif command == 'load_mongodb':
        if len(sys.argv) < 3:
            print("Usage: python table_insert.py load_mongodb <json_file> <collection_name>")
            sys.exit(1)
        json_file = sys.argv[2]
        collection_name = sys.argv[3]
        insert_json_to_mongodb(json_file, conn_string, db_name, collection_name, db_schema)
    
    else:
        print("Invalid command. Use 'load_sql' or 'load_mongodb'.")