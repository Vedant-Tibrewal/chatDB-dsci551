# dummy utility file for the project
import pandas as pd
import mysql.connector
import json
import re
from collections import defaultdict


def normalize_column_names(df):
    normalized_columns = []
    for col in df.columns:
        normalized_col = col.lower()  # Convert to lower case
        normalized_col = re.sub(r'\s+|\W+', '_', normalized_col)  # Replace spaces and special characters
        normalized_columns.append(normalized_col)
    df.columns = normalized_columns
    return df


def infer_mysql_datatype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'DATETIME'
    else:
        return 'VARCHAR(255)'


def show_tables_and_primary_keys(db_config):
    try:
        # Establish a connection to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Query to retrieve tables and their primary keys
        query = """
        SELECT 
            tab.table_name,
            GROUP_CONCAT(kcu.column_name ORDER BY kcu.ordinal_position SEPARATOR ', ') AS primary_keys
        FROM 
            information_schema.tables tab
        LEFT JOIN 
            information_schema.table_constraints tco
            ON tab.table_schema = tco.table_schema
            AND tab.table_name = tco.table_name
            AND tco.constraint_type = 'PRIMARY KEY'
        LEFT JOIN 
            information_schema.key_column_usage kcu
            ON tco.constraint_schema = kcu.constraint_schema
            AND tco.constraint_name = kcu.constraint_name
            AND tco.table_name = kcu.table_name
        WHERE 
            tab.table_schema = %s
        GROUP BY 
            tab.table_schema,
            tab.table_name
        ORDER BY 
            tab.table_name;
        """

        # Execute the query
        cursor.execute(query, (db_config['database'],))
        
        # Fetch all results
        results = cursor.fetchall()

        pk = []
        # Print the results
        print(f"Tables and Primary Keys in database '{db_config['database']}':")
        for table_name, primary_keys in results:
            pk.append((table_name, primary_keys))
            if primary_keys:
                print(f"Table: {table_name}, Primary Key(s): {primary_keys}")
            else:
                print(f"Table: {table_name}, No Primary Key")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the connection
        if conn.is_connected():
            cursor.close()
            conn.close()

    return pk


def csv_to_json_mongo(csv_file, save_file, primary_key):
    '''
    Convert csv file to mongodb acceptable json file
    '''


    # Read the CSV file using Pandas
    data = pd.read_csv(csv_file)
    
    # Convert the DataFrame to a list of dictionaries (JSON format)
    json_output = data.to_dict(orient='records')
    
    # Convert lists of values into MongoDB accepted format
    json_ready = []
    for record in json_output:
        json_ready.append({key: value for key, value in record.items() if pd.notna(value)})  # remove NaN values
    for record in json_ready:
        record['_id'] = record[primary_key]

    # write_json(json_ready, save_file)
    with open(save_file, 'w') as file:
        json.dump(json_ready, file, indent=4)
    
    return json_ready


def generate_dynamic_schema(input_data):
    # Initialize schema dictionary
    schema = defaultdict(lambda: defaultdict(dict))

    # Function to determine data type
    def determine_data_type(value):
        if isinstance(value, int):
            return "INT"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "VARCHAR(255)"  # Default to VARCHAR for unknown types

    # Process each record in the input data
    for record in input_data:
        collection_name = record.get('collection', 'default_collection')
        for key, value in record.items():
            if key != 'collection':
                schema[collection_name][key] = determine_data_type(value)

        # Add primary key and foreign keys (assuming 'id' as primary key)
        schema[collection_name]['pk'] = ['_id']
        schema[collection_name]['fk'] = {}  # Add foreign keys if needed

    return dict(schema)
