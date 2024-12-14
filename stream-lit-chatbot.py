import streamlit as st
import pandas as pd
import mysql.connector
import random
import re
from pymongo import MongoClient
import ast

from src.chatdb.core.query_generator import QueryGenerator
from src.chatdb.mysql.sql_generator import SQLGenerator
from src.chatdb.mongodb.nosql_generator import NoSQLGenerator
from src.chatdb.core.io import read_json
from src.chatdb.constants.sample_queries import *


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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    primary_keys = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
        pk = cursor.fetchone()
        if pk:
            primary_keys.append((table_name, pk[4]))
    cursor.close()
    conn.close()
    return primary_keys

def get_database_info(dbconfig):
    try:
        connection = mysql.connector.connect(
            **dbconfig
        )
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Get schema for each table
        schema_info = {}
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            schema_info[table] = cursor.fetchall()

        return tables, schema_info
    except Exception as e:
        return [], {}
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def sample_sql_queries(prompt):
    if prompt.strip().upper().startswith('SAMPLE'):
            # cursor.execute("SHOW TABLES")
            # tables = [table[0] for table in cursor.fetchall()]
        if "join" in prompt:
            samples = random.choice(JOIN)
            if samples:
                st.write("Sample Queries based on Join:")
                # for sample in samples:
                st.code(samples)
            return samples
        elif "group by" in prompt:
            samples = random.choice(GROUP_BY)
            if samples:
                st.write("Sample Queries based on group_by:")
                # for sample in samples:
                st.code(samples)
            return samples
        elif "order by" in prompt:
            samples = random.choice(ORDER_BY)
            if samples:
                st.write("Sample Queries based on order_by:")
                # for sample in samples:
                st.code(samples)
            return samples
        elif "limit" in prompt:
            samples = random.choice(LIMIT)
            if samples:
                st.write("Sample Queries based on limit:")
                # for sample in samples:
                st.markdown(f"- {samples}")
            return samples
        else:
            samples = random.choice(WHERE)
            if samples:
                st.write("Sample Queries based on Where:")
                # for sample in samples:
                st.code(samples)
            return samples
    else:
        return prompt
    

def execute_mongo_queries(query_strings, mongo_uri='mongodb://localhost:27017/', db_name='chatdb'):
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Extract collection name and command
    match = re.search(r"db\.(\w+)\.(find|aggregate)\((.*)\)$", query_strings, re.DOTALL)
    if not match:
        return []
    
    collection_name, command_type, command_body = match.groups()

    collection = db[collection_name]

    # Process find queries
    if command_type == 'find':
        filter_match = re.search(r"find\((.*?)\)(?:\.sort|\.|$)", query_strings, re.DOTALL)
        sort_match = re.search(r"\.sort\((.*?)\)", query_strings)
        limit_match = re.search(r"\.limit\((\d+)\)", query_strings)
        
        filter_str = filter_match.group(1) if filter_match else "{}"
        sort_str = sort_match.group(1) if sort_match else None
        limit = int(limit_match.group(1)) if limit_match else None
        
        # result = f"Find in {collection} with filter: {filter_str}"
        if sort_str and limit:
            results = collection.find(eval(filter_str)).sort(eval(sort_str)).limit(limit)
        elif limit:
            results = collection.find(eval(filter_str)).limit(limit)
        elif sort_str:
            results = collection.find(eval(filter_str)).sort(eval(sort_str))
        else:
            results = collection.find(eval(filter_str))
        
    # Process aggregate queries
    elif command_type == 'aggregate':
        pipeline = command_body.strip()
        st.markdown(pipeline)
        results = collection.aggregate(eval(pipeline))
        # result = f"Aggregate in {collection} with pipeline: {pipeline}"
    
    return results


def sample_mongo_queries(prompt):
    if prompt.strip().upper().startswith('SAMPLE'):
        if "group" in prompt:
            query = random.choice(GROUP)
            if query:
                st.write("Sample Queries based on group:")
                # for sample in query:
                st.code(query)
                result = execute_mongo_queries(query)
            return result
        elif "sort" in prompt:
            query = random.choice(SORT)
            if query:
                st.write("Sample Queries based on sort:")
                # for sample in query:
                st.code(query)
                result = execute_mongo_queries(query)
            return result
        elif "limit" in prompt:
            query = random.choice(MONGO_LIMIT)
            if query:
                st.write("Sample Queries based on limit:")
                # for sample in query:
                st.code(query)
                result = execute_mongo_queries(query)
            return result
        else:
            query = random.choice(FILTER)
            if query:
                st.write("Sample Queries based on Filter:")
                # for sample in query:
                st.code(query)
                result = execute_mongo_queries(query)
            return result
    else:
        return prompt


def execute_sql_query(dbconfig, query):
    try:
        connection = mysql.connector.connect(
            **dbconfig
        )
        cursor = connection.cursor()
        schema_info = {}
        # For SELECT queries
        if query.strip().upper().startswith('SELECT'):
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df)
            return df, None
        elif query.strip().upper().startswith('SHOW'):
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            if tables:
                st.write("Tables in the database:")
                for table in tables:
                    st.markdown(f"- {table}")
            return df_schema, None
        
            # results = cursor.fetchall()
        elif query.strip().upper().startswith('DESCRIBE'):  # Fixed typo here
            cursor.execute(query)
            schema_info['table'] = cursor.fetchall()
            df_schema = pd.DataFrame(
                    schema_info['table'], 
                    columns=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
                )
            st.dataframe(df_schema)
            return df_schema, None
        # For other queries (INSERT, UPDATE, DELETE)
        else:
            connection.commit()
            st.markdown("Query format not supported")
            return pd.DataFrame(), None
            
    except Exception as e:
        return None, str(e)
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def create_chatbot(sql_config, mongo_uri, db_schema):
    st.set_page_config(page_title="Database Explorer", page_icon="🔍", layout="wide")

    # Main content area
    st.title("ChatDB")
    
    # Create tabs for different interfaces
    tab1, tab2 = st.tabs(["SQL", "MongoDB"])
    
    with tab1:
        col1, col2 = st.columns([1, 3])
        # Get database information
        tables, schema_info = get_database_info(sql_config)
        
        # Sidebar with database information
        with col1:
            
            st.title("Database Explorer")
            
            # Display available tables
            st.subheader("Available Tables")
            for table in tables:
                with st.expander(table):
                    # Display schema
                    df_schema = pd.DataFrame(
                        schema_info[table], 
                        columns=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
                    )
                    st.dataframe(df_schema)
            
            # Sample queries section
            st.subheader("Sample Queries")
            
            # Basic queries
            with st.expander("Basic Queries"):
                for table in tables:
                    st.code(f"SELECT * FROM {table} LIMIT 5")
                    st.code(f"SELECT COUNT(*) FROM {table}")
            
        with col2:
            sql_generator = SQLGenerator(db_schema)
            greetings = ["Hi, How can i help you today?",
                     "Hola, How can I help you with the database today?",
                    "Welcome to ChatDB! I'm here to help you learn about querying databases. What would you like to explore today?",
                    "Hello! I'm your database assistant. Would you like to explore a database, see some sample queries, or ask a question in natural language?",
"Greetings! I'm ChatDB, your interactive database query helper. How can I assist you with your database learning journey?",
"Hi there! Ready to dive into the world of databases? Let me know if you'd like to see some sample queries or explore a specific database.",
"Welcome to the world of data! I'm here to help you master database queries. What aspect of database querying would you like to start with?",
                     ]
            msg = random.choice(greetings)
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": msg}
                ]

            tables.insert(0, "Any")
            table = st.selectbox('Choose an table:', tables)

            if table=="Any":
                table=None
            
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask about the database..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate and display response
                with st.chat_message("assistant"):
                    try:
                        if "sample" in prompt:
                            query = sample_sql_queries(prompt)
                        else:
                            query = sql_generator.sql_parser(prompt, table)
                            st.markdown("Converted into query")
                            st.code(query)
                            st.markdown("Now executing")
                        # Execute the query
                        result = execute_sql_query(sql_config, query)
                    
                        # Generate a response message
                        response = "Query executed successfully. Here are the results:"
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_message = f"Error executing query: {str(e)}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    with tab2:
        col1, col2 = st.columns([1,3])

        client = MongoClient(mongo_uri)
        db = client['chatdb']
        collections = db.list_collection_names()
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.title("MongoDB Explorer")
            
            # Display available collections
            st.subheader("Available Collections")
            for collection in collections:
                with st.expander(collection):
                    # Display sample document
                    sample_doc = db[collection].find_one()
                    st.json(sample_doc)
            
            # Sample queries section
            st.subheader("Sample Queries")
            
            # Basic queries
            with st.expander("Basic Queries"):
                for collection in collections:
                    st.code(f"db.{collection}.find().limit(5)")
                    st.code(f"db.{collection}.count()")
                
                if len(collections) > 1:
                    st.code(f"""
                        db.{collections[0]}.aggregate([
                            {{"$lookup": {{
                                "from": "{collections[1]}",
                                "localField": "field_name",
                                "foreignField": "field_name",
                                "as": "joined_data"
                            }}}}
                        ])
                    """)
        
            with col2:
                db = "chatdb"

                collections.insert(0, "Any")
                # st.markdown(collections)

                collection = st.selectbox("Choose a collection:", collections)
                
                if collection == "Any":
                    collection = None
                
                mongodb_generator = NoSQLGenerator(db_schema, mongo_uri, db)
                greetings = [
                    "Hi, How can I help you today?",
                    "Hola, How can I help you with the MongoDB database today?",
                    "Welcome to ChatMongoDB! I'm here to help you learn about querying MongoDB. What would you like to explore today?",
                    "Hello! I'm your MongoDB assistant. Would you like to explore a collection, see some sample queries, or ask a question in natural language?",
                    "Greetings! I'm ChatMongoDB, your interactive database query helper. How can I assist you with your MongoDB learning journey?",
                    "Hi there! Ready to dive into the world of MongoDB? Let me know if you'd like to see some sample queries or explore a specific collection.",
                    "Welcome to the world of document databases! I'm here to help you master MongoDB queries. What aspect of MongoDB querying would you like to start with?",
                ]
                msg = random.choice(greetings)
                if "messages" not in st.session_state:
                    st.session_state.messages = [
                        {"role": "assistant", "content": msg}
                    ]
                
                # Display chat messages
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                
                # Chat input
                if prompt := st.chat_input("Ask about the MongoDB database..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    # Generate and display response
                    with st.chat_message("assistant"):
                        try:
                            if "sample" in prompt:
                                result = sample_mongo_queries(prompt)
                            else:
                                query, result = mongodb_generator.mongod_parser(prompt, collection)
                                st.markdown("Converted into query")
                                st.code(query)
                                st.markdown("Now executing")
                            
                            # Convert result to DataFrame
                            df = pd.DataFrame(list(result))
                            
                            # Display the result
                            st.dataframe(df)
                            
                            # Generate a response message
                            response = f"Query executed successfully. Here are the results:"
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Add download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download Results",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            error_message = f"Error executing query: {str(e)}"
                            st.error(error_message)
                            st.session_state.messages.append({"role": "assistant", "content": error_message})


if __name__ == "__main__":
    conn_string = "mongodb://localhost:27017/"
    db_name = "chatdb"
    coll_name = "patients"
    mysql_configs = read_json("src/chatdb/constants/config.json")
    db_schema = read_json("src/chatdb/constants/db_schema.json")
    create_chatbot(sql_config=mysql_configs, mongo_uri=conn_string, db_schema=db_schema)