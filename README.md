# chatDB-dsci551
The goal of this project is to develop ChatDB, an interactive ChatGPT-like application that assists users in learning how to query data in database systems, including SQL and NoSQL databases.

---
<br>

```python
import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

# Sample data (you should replace this with your own dataset)
english_texts = [
    "Show me all employees",
    "Find employees with salary greater than 50000",
    "List names of female employees"
]
sql_queries = [
    "SELECT * FROM employees",
    "SELECT * FROM employees WHERE salary > 50000",
    "SELECT name FROM employees WHERE gender = 'female'"
]

# Tokenize input and output texts
input_tokenizer = Tokenizer()
output_tokenizer = Tokenizer()

input_tokenizer.fit_on_texts(english_texts)
output_tokenizer.fit_on_texts(sql_queries)

input_sequences = input_tokenizer.texts_to_sequences(english_texts)
output_sequences = output_tokenizer.texts_to_sequences(sql_queries)

# Pad sequences
max_input_length = max(len(seq) for seq in input_sequences)
max_output_length = max(len(seq) for seq in output_sequences)

input_sequences = pad_sequences(input_sequences, maxlen=max_input_length, padding='post')
output_sequences = pad_sequences(output_sequences, maxlen=max_output_length, padding='post')

# Convert output sequences to numpy array
output_sequences = np.array(output_sequences)

# Model parameters
input_vocab_size = len(input_tokenizer.word_index) + 1
output_vocab_size = len(output_tokenizer.word_index) + 1
embedding_dim = 256
lstm_units = 256

# Define the model
encoder_inputs = Input(shape=(None,))
encoder_embedding = Embedding(input_vocab_size, embedding_dim)(encoder_inputs)
encoder_lstm = LSTM(lstm_units, return_state=True)
encoder_outputs, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(None,))
decoder_embedding = Embedding(output_vocab_size, embedding_dim)
decoder_lstm = LSTM(lstm_units, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embedding(decoder_inputs), initial_state=encoder_states)
decoder_dense = Dense(output_vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Prepare decoder input data
decoder_input_data = np.zeros_like(output_sequences)
decoder_input_data[:, 1:] = output_sequences[:, :-1]

# Train the model
model.fit([input_sequences, decoder_input_data], output_sequences,
          batch_size=64, epochs=100, validation_split=0.2)

# Function to translate English to SQL
def translate_english_to_sql(input_text):
    input_seq = input_tokenizer.texts_to_sequences([input_text])
    input_seq = pad_sequences(input_seq, maxlen=max_input_length, padding='post')
    
    target_seq = np.zeros((1, 1))
    target_seq[0, 0] = output_tokenizer.word_index['start']  # Assume 'start' token exists
    
    output_seq = []
    
    while True:
        output_tokens, h, c = model.predict([input_seq, target_seq])
        predicted_token = np.argmax(output_tokens[0, -1, :])
        output_seq.append(predicted_token)
        
        if predicted_token == output_tokenizer.word_index['end'] or len(output_seq) > max_output_length:
            break
        
        target_seq = np.zeros((1, 1))
        target_seq[0, 0] = predicted_token
    
    return ' '.join([output_tokenizer.index_word[token] for token in output_seq])

# Test the model
test_input = "Show employees with salary less than 40000"
print(translate_english_to_sql(test_input))
```

This code provides a basic implementation of a sequence-to-sequence model for translating English to SQL queries. Here's a breakdown of what the code does:

1. We define sample English texts and corresponding SQL queries.
2. We tokenize and pad the input and output sequences.
3. We define the model architecture using an encoder-decoder LSTM structure.
4. We compile and train the model.
5. We create a function `translate_english_to_sql` to use the trained model for translation.

Please note that this is a simplified example and may not produce perfect results. To improve the model, you should consider the following:

1. Use a larger and more diverse dataset.
2. Implement attention mechanisms for better performance.
3. Use pre-trained word embeddings.
4. Implement beam search for better decoding.
5. Fine-tune hyperparameters.
6. Consider using more advanced architectures like Transformer models.

Remember that training such a model requires a substantial amount of data and computational resources. You may need to adjust the model architecture and training parameters based on your specific requirements and available resources.

Citations:
[1] https://stackoverflow.com/questions/54819075/what-are-some-of-the-ways-to-convert-nlp-to-sql
[2] https://towardsdatascience.com/natural-language-to-sql-from-scratch-with-tensorflow-adf0d41df0ca?gi=91ae95d0479f
[3] https://stackoverflow.com/questions/49199943/not-able-to-generate-correct-english-to-sql-translations-using-lstm-for-machine
[4] https://openreview.net/pdf/009190562cd7bcddd5981bfe888cd6c1e44e1aa8.pdf

--------
-------

## custom stop word and substitute words

Based on the questions in the dataset, here are some suggestions for custom stop words and substitutions to help with building a custom NER model for classifying SQL query clauses:

Stop words to consider removing:

- Common question words: What, How, Which, Who, When, Where, Why, List, Show, Find, Give, Return
- Articles: a, an, the
- Prepositions: of, in, by, for, with, to, from, on, at
- Conjunctions: and, or, but
- Auxiliary verbs: is, are, was, were, do, does, did
- Generic verbs: have, has, had, be, been

a, an, the
is, are, was, were
and, or, but
of, in, by, for, with, to, from
how, many, what, which, who, whose, where, when
do, we, have, show, list, find, give, return, select
all, every, each, some, any
that, there, it, they, them
be, been, being
can, could, would, should
not, no
more, most, less, least
only, except
both, either
please

Substitutions to consider:

- Replace specific entity names with generic placeholders:
  - Person names -> PERSON
  - Place names -> PLACE
  - Organization names -> ORG
  - Numbers -> NUMBER

- Replace specific field/column names with generic placeholders:
  - name -> NAME
  - id -> ID
  - date -> DATE
  - price -> PRICE
  - count -> COUNT
  
Certainly! Here's a more exhaustive list of words and phrases that can be used for substitution in SQL query classification:

Comparison Words:
- Greater than, more than, above, over, exceeding, surpassing, beyond -> GREATER
- Less than, fewer than, below, under, beneath, lower than -> LESS
- Equal to, same as, identical to, matching -> EQUAL
- Not equal to, different from, excluding -> NOT_EQUAL
- Greater than or equal to, at least -> GREATER_EQUAL
- Less than or equal to, at most -> LESS_EQUAL
- Between, in the range of -> BETWEEN
- In, within, among -> IN
- Not in, outside of -> NOT_IN
- Like, similar to -> LIKE
- Not like, dissimilar to -> NOT_LIKE

Aggregation Functions:
- Average, mean, typical -> AVG
- Maximum, highest, most, top, peak, greatest -> MAX
- Minimum, lowest, least, bottom, smallest -> MIN
- Total, sum, aggregate, combined -> SUM
- Count, number of, quantity of -> COUNT
- Distinct count, unique count -> COUNT_DISTINCT

Ordering Terms:
- Ascending, alphabetical, increasing, from lowest to highest -> ASC
- Descending, reverse alphabetical, decreasing, from highest to lowest -> DESC

Logical Operators:
- And, also, as well as, in addition to -> AND
- Or, alternatively, either -> OR
- Not, except, excluding -> NOT

Set Operations:
- Union, combine, merge -> UNION
- Intersect, in common, shared by -> INTERSECT
- Except, subtract, exclude -> EXCEPT

Grouping:
- Group by, categorize by, classify by -> GROUP BY
- Having -> HAVING

Joining:
- Join, combine, merge -> JOIN
- Inner join -> INNER JOIN
- Left join, left outer join -> LEFT JOIN
- Right join, right outer join -> RIGHT JOIN
- Full join, full outer join -> FULL JOIN

Limiting:
- Limit, top, first -> LIMIT

Distinct:
- Unique, distinct, different -> DISTINCT

Null Handling:
- Is null, is empty, is missing -> IS NULL
- Is not null, has value, is present -> IS NOT NULL

Date Functions:
- Year, annual -> YEAR
- Month, monthly -> MONTH
- Day, daily -> DAY
- Date, on the date -> DATE

String Functions:
- Concatenate, combine strings -> CONCAT
- Substring, part of string -> SUBSTRING
- Length, size of string -> LENGTH
- Upper case, capitalize -> UPPER
- Lower case -> LOWER

This list covers a wide range of SQL concepts and their natural language equivalents. Using these substitutions can help in standardizing and classifying natural language queries for SQL generation.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/36168381/03dbd2ac-9fa0-4ba9-a0fe-3b3d47759b6e/word_bank.json
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/36168381/ad1c0ef2-55ec-48a0-b5a2-a44f98147168/test.csv
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/36168381/2773233e-c000-41f2-a275-272d36e692ae/train.csv
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_7496fd79-9202-4f81-9181-06e7808f9934/37769e98-d3d3-4ae6-9d95-bfa0c0e18242/validation.csv
[5] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_7496fd79-9202-4f81-9181-06e7808f9934/cba70d55-a125-4aef-8d12-e34572590283/551-fa24-project-guideline.pdf

Some example substitutions:

"What is the name of the oldest student?"
-> "NAME of GREATER AGE student"

"How many orders were placed by customers in New York?"
-> "COUNT orders PLACE customers"

"List the product names with prices higher than $100."
-> "NAME products PRICE GREATER NUMBER"

The key is to generalize common patterns while preserving the important semantic elements related to SQL query structure. You may need to experiment to find the right balance of substitution vs. preserving details for your specific use case.

Does this help explain some ways you could customize the text processing for SQL query classification? Let me know if you need any clarification or have additional questions!

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/36168381/ad1c0ef2-55ec-48a0-b5a2-a44f98147168/test.csv
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/36168381/2773233e-c000-41f2-a275-272d36e692ae/train.csv
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_7496fd79-9202-4f81-9181-06e7808f9934/37769e98-d3d3-4ae6-9d95-bfa0c0e18242/validation.csv
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_7496fd79-9202-4f81-9181-06e7808f9934/cba70d55-a125-4aef-8d12-e34572590283/551-fa24-project-guideline.pdf


------
-----
## Aggregate function mapping
```
aggregate_functions = {
    'COUNT': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'TIMESTAMP', 'BOOLEAN'],
        'Python': ['int', 'float', 'str', 'bool', 'datetime.date', 'datetime.datetime', 'list', 'tuple', 'dict', 'set']
    },
    'SUM': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL'],
        'Python': ['int', 'float']
    },
    'AVG': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL'],
        'Python': ['int', 'float']
    },
    'MIN': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'TIMESTAMP'],
        'Python': ['int', 'float', 'str', 'datetime.date', 'datetime.datetime']
    },
    'MAX': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'TIMESTAMP'],
        'Python': ['int', 'float', 'str', 'datetime.date', 'datetime.datetime']
    },
    'DISTINCT': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'TIMESTAMP', 'BOOLEAN'],
        'Python': ['int', 'float', 'str', 'bool', 'datetime.date', 'datetime.datetime', 'tuple']
    },
    'GROUP_CONCAT': {
        'SQL': ['VARCHAR', 'CHAR', 'TEXT'],
        'Python': ['str']
    },
    'FIRST': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'TIMESTAMP', 'BOOLEAN'],
        'Python': ['int', 'float', 'str', 'bool', 'datetime.date', 'datetime.datetime']
    },
    'LAST': {
        'SQL': ['INTEGER', 'FLOAT', 'DECIMAL', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'TIMESTAMP', 'BOOLEAN'],
        'Python': ['int', 'float', 'str', 'bool', 'datetime.date', 'datetime.datetime']
    }
}
```

----
----
## SUBSTITUTE WORDS

```
aggregate_functions = {
    'COUNT': ['count', 'number of', 'quantity of', 'total number of', 'tally', 'enumerate', 'how many'],
    'SUM': ['sum', 'total', 'aggregate', 'combined', 'add up', 'overall', 'cumulative'],
    'AVG': ['average', 'mean', 'typical', 'median', 'expected value', 'norm', 'central tendency'],
    'MAX': ['maximum', 'highest', 'most', 'top', 'peak', 'greatest', 'largest', 'biggest', 'uppermost'],
    'MIN': ['minimum', 'lowest', 'least', 'bottom', 'smallest', 'tiniest', 'least', 'floor'],
    'DISTINCT': ['unique', 'different', 'distinct', 'individual', 'separate', 'non-duplicate', 'exclusive'],
    'GROUP_CONCAT': ['concatenate', 'combine strings', 'join', 'merge text', 'string aggregation', 'text combination'],
    'FIRST': ['first', 'initial', 'earliest', 'primary', 'leading', 'opening', 'foremost'],
    'LAST': ['last', 'final', 'latest', 'ultimate', 'concluding', 'terminal', 'closing']
}

comparison_operators = {
    'GREATER': ['greater than', 'more than', 'above', 'over', 'exceeding', 'surpassing', 'beyond', 'higher than', 'in excess of'],
    'LESS': ['less than', 'fewer than', 'below', 'under', 'beneath', 'lower than', 'not as much as', 'smaller than'],
    'EQUAL': ['equal to', 'same as', 'identical to', 'matching', 'equivalent to', 'corresponds to', 'is'],
    'NOT_EQUAL': ['not equal to', 'different from', 'excluding', 'not the same as', 'dissimilar to', 'unlike', 'other than'],
    'GREATER_EQUAL': ['greater than or equal to', 'at least', 'no less than', 'minimum of', 'not below', 'from'],
    'LESS_EQUAL': ['less than or equal to', 'at most', 'no more than', 'maximum of', 'not above', 'up to'],
    'BETWEEN': ['between', 'in the range of', 'from ... to', 'within the bounds of', 'inside the limits of'],
    'IN': ['in', 'within', 'among', 'included in', 'part of', 'contained in', 'one of'],
    'NOT_IN': ['not in', 'outside of', 'excluded from', 'not among', 'not part of', 'not contained in'],
    'LIKE': ['like', 'similar to', 'resembling', 'matching pattern', 'corresponding to'],
    'NOT_LIKE': ['not like', 'dissimilar to', 'unlike', 'not matching pattern', 'different from pattern']
}

logical_operators = {
    'AND': ['and', 'also', 'as well as', 'in addition to', 'plus', 'together with', 'along with', 'including'],
    'OR': ['or', 'alternatively', 'either', 'otherwise', 'else', 'and/or'],
    'NOT': ['not', 'except', 'excluding', 'other than', 'but not', 'save for', 'apart from']
}

sql_clauses = {
    'SELECT': ['show', 'display', 'list', 'give', 'return', 'fetch', 'retrieve', 'get', 'find', 'what is', 'what are'],
    'FROM': ['from', 'in', 'out of', 'sourced from', 'derived from', 'based on'],
    'WHERE': ['where', 'for which', 'that have', 'meeting the condition', 'satisfying', 'fulfilling'],
    'GROUP BY': ['group by', 'categorize by', 'classify by', 'organize by', 'arrange by', 'cluster by'],
    'HAVING': ['having', 'with the condition', 'subject to', 'meeting the criteria'],
    'ORDER BY': ['order by', 'sort by', 'arrange by', 'rank by', 'sequence by'],
    'LIMIT': ['limit', 'top', 'first', 'restrict to', 'cap at', 'only show'],
    'JOIN': ['join', 'combine', 'merge', 'connect', 'link', 'associate'],
    'UNION': ['union', 'combine', 'merge', 'incorporate', 'consolidate', 'unite'],
    'INTERSECT': ['intersect', 'in common', 'shared by', 'mutual', 'overlapping'],
    'EXCEPT': ['except', 'subtract', 'exclude', 'remove', 'omit', 'leave out']
}

data_types = {
    'INTEGER': ['integer', 'int', 'whole number', 'numeric'],
    'FLOAT': ['float', 'decimal', 'real number', 'fractional number'],
    'VARCHAR': ['string', 'text', 'characters', 'alphanumeric'],
    'DATE': ['date', 'calendar day', 'day'],
    'TIMESTAMP': ['timestamp', 'date and time', 'moment', 'point in time'],
    'BOOLEAN': ['boolean', 'true/false', 'yes/no', 'binary']
}

stop_words = [
    'a', 'an', 'the',
    'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'we', 'us', 'our', 'ours', 'ourselves', 'they', 'them', 'their', 'theirs', 'themselves',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'do', 'does', 'did', 'have', 'has', 'had', 'can', 'could', 'shall', 'should', 'will', 'would', 'may', 'might', 'must',
    'about', 'across', 'after', 'against', 'along', 'around', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'during', 'into', 'near', 'off', 'out', 'through', 'toward', 'under', 'up', 'with',
    'if', 'then', 'because', 'as', 'until', 'while',
    'this', 'that', 'these', 'those', 'such', 'what', 'which', 'whose', 'whoever', 'whatever', 'whichever', 'whomever', 'either', 'neither', 'both',
    'very', 'really', 'always', 'never', 'too', 'already', 'often', 'sometimes', 'rarely', 'seldom', 'again', 'further', 'then', 'once', 'here', 'there', 'where', 'why', 'how',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth',
    'few', 'little', 'much', 'enough',
    'yes', 'no', 'not', 'okay', 'ok', 'right', 'sure', 'well', 'uh', 'um', 'oh', 'eh', 'hmm', 'just', 'ever', 'yet', 'etc', 'perhaps', 'maybe', 'list'
]
```
---------
--------
Database
2 dictionaries
1 with datatype  
```
SQL = {
    table1: {
        pk : [], # composite possible
        fk : {table_b: "col_name"},
        col_1: datatype
        col_2: datatype
    },
}


"Hospital_Admissions": {
    "pk": ["AdmissionID"],
    "fk": {"Patients": "PatientID"},
    "AdmissionID": "INT",
    "PatientID": "INT",
    "Doctor": "VARCHAR(255)",
    "Hospital": "VARCHAR(255)",
    "Date_of_Admission": "DATE",
    "Discharge_Date": "DATE",
    "Room_Number": "INT",
    "Admission_Type": "VARCHAR(50)"
}

"Patients": {
    "pk": ["PatientID"],
    "fk": {},
    "PatientID": "INT",
    "Name": "VARCHAR(255)",
    "Age": "INT",
    "Gender": "VARCHAR(10)",
    "Blood_Type": "VARCHAR(5)",
    "Medical_Condition": "VARCHAR(255)"
}

"Insurance": {
    "pk": ["InsuranceID"],
    "fk": {"Patients": "PatientID"},
    "InsuranceID": "INT",
    "PatientID": "INT",
    "Insurance_Provider": "VARCHAR(255)",
    "Billing_Amount": "DECIMAL(10, 2)",
    "Medication": "VARCHAR(255)",
    "Test_Results": "VARCHAR(50)"
}


# col names in key, dataype as value
mongodb_database = {
    "users": {
        "pk": ["_id"],
        "fk": {},
        "_id": "ObjectId",
        "username": "String",
        "email": "String",
        "age": "Number",
        "birth_date": "Date",
        "created_at": "Date",
        "is_active": "Boolean"
    },
    "orders": {
        "pk": ["_id"],
        "fk": {"users": "user_id"},
        "_id": "ObjectId",
        "user_id": "ObjectId",
        "quantity": "Number",
        "total_amount": "Number",
        "order_date": "Date",
        "status": "String",
        "items": "Array"
    },
    "products": {
        "pk": ["_id"],
        "fk": {},
        "_id": "ObjectId",
        "name": "String",
        "description": "String",
        "price": "Number",
        "stock": "Number",
        "categories": "Array",
        "tags": "Array"
    }
}