# chatDB-dsci551
The goal of this project is to develop ChatDB, an interactive ChatGPT-like application that assists users in learning how to query data in database systems, including SQL and NoSQL databases.

---
## FOLDER STURCTURE

- dataset: Contains the data files used by the project.
- docs: Holds documentation files for the project.
- environments: Contains environment configuration files, such as env.yml for managing project dependencies.
- notebooks: Stores Jupyter notebooks used for exploration.
- src: The main source code directory for the ChatDB project.
  - chatdb: The core package of the project.
    - constants: Contains configuration files, constants, and sample queries.
    - core: Holds core functionality files like input/output operations, query generation, and utility functions.
    - mongodb: Contains files related to NoSQL (MongoDB) query generation.
    - mysql: Contains files related to SQL (MySQL) query generation.

## INSTALLATION
In Environments folder use `env.yml` file to create the conda environemnts

Run this command to create environments
`conda env create -f env.yml`

Run this command to activate environment
`conda activate chatdb`

Run this command inside the folder to install the project pip package
`pip install -e .`


## STEPS TO INSERT DATA

- use csv file for mysql database
- use json file for mongodb database

Use this command in terminal to insert data
`python table_insert {load_sql|load_mongodb} {file_path} {table_name|collection_name}`

## STEPS TO QUERY USING CHATDB

- Make sure your conda env is activated

Use this command to run frontend to query database
`streamlit run stream-lit-chatbot.py`

## Some Sample queries

User can request for sample queires for both SQL and MongoDB database like
- For SQL \
`Sample Queries using {WHERE | LIMIT | ORDER BY | GROUP BY | JOIN} `

- For MongoDB \
- `Sample queries for {FILTER | GROUP | SORT | LIMIT}`


```
- List all hospital names and doctors.
- Show all patients names where age greater than 60.
- Give the count of patients grouped by bloodtype.
- Retrieve all insurance providers and associated patientnames.
- Find the number of patients grouped by gender.
- List all hospital names and patient names.
- number of patients grouped by disease
```


