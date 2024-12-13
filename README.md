# chatDB-dsci551
The goal of this project is to develop ChatDB, an interactive ChatGPT-like application that assists users in learning how to query data in database systems, including SQL and NoSQL databases.

---
## FOLDER STURCTURE

## INSTALLATION
In Environments folder use `env.yml` file to create the conda environemnts

Run this command to create environments
`conda env create -f env.yml`

Run this command to activate environment
`conda activate chatdb`


## STEPS TO INSERT DATA

- use csv file for mysql database
- use json file for mongodb database

Use this command in terminal to insert data
`python table_insert {load_sql|load_mongodb} {file_path} {table_name|collection_name}`

## STEPS TO QUERY USING CHATDB

- Make sure your conda env is activated

Use this command to run frontend to query database
`streamlit run stream-lit-chatbot.py`
