import re
from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
# import pandas as pd
from difflib import get_close_matches
from thefuzz import fuzz
import networkx as nx
import heapq
from collections import defaultdict
from ordered_set import OrderedSet
from collections import Counter
from word2number import w2n

from src.chatdb.constants.constants import CONSTANTS, QUERY_TEMPLATE
from src.chatdb.core.io import read_json

lemmatizer = WordNetLemmatizer()

class QueryGenerator:
    def __init__(self, db_schema):
        self.db_schema = db_schema
        self.req_schema = dict()
        self.constants = CONSTANTS
        self.query_template = QUERY_TEMPLATE

    def replace_string(self, text, replace_dict):
        # Create a reverse mapping from values to keys
        value_to_key = {}
        for key, values in replace_dict.items():
            for value in values:
                value_to_key[value.lower()] = key.lower()
        
        # Create a regex pattern for matching words
        pattern = r'\b(' + '|'.join(re.escape(word) for word in value_to_key.keys()) + r')\b'
        
        # Function to replace matched words
        def replace_word(match):
            return value_to_key.get(match.group(0).lower(), match.group(0))
        
        # Perform the replacement
        replaced_text = re.sub(pattern, replace_word, text, flags=re.IGNORECASE)
    
        return replaced_text

    def replace_numbers(self, token):
        try:
            return w2n.word_to_num(token)
        except:
            return token
        
    def merge_before_token(self, tokens, merge_key):

        result = []
        i = 0

        while i < len(tokens) - 1:  # Changed to len(tokens) - 1
            if tokens[i].lower() not in self.constants['ALL_KEYWORDS'] and (tokens[i + 1].lower() == merge_key or tokens[i + 1].lower() == f"{merge_key}s"):
                result.append(f"{tokens[i]}_{tokens[i+1]}")
                i += 2
            else:
                result.append(tokens[i])
                i += 1
        if i < len(tokens):  # Add any remaining token
            result.append(tokens[i])

        return result

    def preprocess_text(self, text):

        text = re.sub(r'\?', '', text)
        text = re.sub(r'\$', '', text)
        text = re.sub(r'\.$', '', text)
        text = re.sub(r',', '', text)
        pattern = r'\b(\d+)-(\d+)\b' # dates 2023-2025 ==> 2023 to 2025
        text = re.sub(pattern, r'\1 to \2', text)


        tokens = text.split()

        result = self.merge_before_token(tokens, merge_key="name") # patients name => patients_name

        result = self.merge_before_token(result, merge_key="date") # intake date => intake_date

        i = 0
        result2 = []

        # differentiate between order by and group by
        order_by_keys = self.constants['sql_clauses']['ORDER BY']
        order_by_keys = [key.split('by')[0].strip() for key in order_by_keys if key.split('by')[0] != '']

        while i < len(result) - 1:
            if result[i+1].lower() =='by' and result[i].lower() in order_by_keys:
                result2.append(f"{result[i]} {result[i+1]}")
                i += 2
            else:
                result2.append(result[i])
                i += 1
        if i < len(result):  # Add any remaining token
            result2.append(result[i])

        text = ' '.join(result2)

        # substitute words
        text = self.replace_string(text, self.constants['sql_clauses'])
        text = self.replace_string(text, self.constants['aggregate_functions'])
        text = self.replace_string(text, self.constants['comparison_operators'])
        between_pattern = r'from \b(\w+|\d+)\b to \b(\w+|\d+)\b | \b(\w+|\d+)\b to \b(\w+|\d+)\b'
        text = re.sub(between_pattern, r" between(\1, \2)", text)
        text = self.replace_string(text, self.constants['logical_operators'])

        # Tokenization
        tokens = text.split()

        tokens = [str(self.replace_numbers(token)) for token in tokens]

        # Remove stopwords
        tokens = [token for token in tokens if token.lower() not in self.constants['stop_words']]


        # Lemmatization // important for similarity
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def remove_keywords(self, tokens):
        token_without_key = [token for token in tokens if token not in self.constants['ALL_KEYWORDS']]

        return token_without_key
    
    def identify_group_by(self, tokens):
        result = []
        i = 0
        while i < len(tokens) - 2:

            if tokens[i].lower() == "group" and tokens[i+1].lower() == "by":

                for table, columns in self.db_schema.items():
                    match = get_close_matches(tokens[i+2], columns)
                    if match:
                        self.query_template["GROUP BY"] = f"{match[0]}"                   
                        result.append(f"{tokens[i]} {tokens[i+1]} {match[0]}")
                        break
                i += 3
            else:
                result.append(tokens[i])
                i += 1
        if i < len(tokens):  # Add any remaining token
            result.extend(tokens[i:])

        return result
    
        # group by before this
    def indentify_table(self, tokens):
        
        detected_table = [[], [], []] # [[table names], [similarities], [tokens]]
        
        for i, token in enumerate(tokens):
            if token.lower() == "from":
                table_name = tokens[i + 1]
                if table_name in self.db_schema:
                    print(f"Table identified: {table_name}")
                    return table_name
            
            for table in self.db_schema.keys():
                similarity = fuzz.ratio(token, table.lower())
                if token in detected_table[2]:
                    i = detected_table[2].index(token)
                    if similarity >= detected_table[1][i]:
                        detected_table[1][i] = similarity
                        detected_table[0][i] = table
                else:
                    if similarity >= 70: # initial threshold
                        detected_table[0].append(table)
                        detected_table[1].append(similarity)
                        detected_table[2].append(token)


        for i in range(len(detected_table[0])):
            if detected_table[1][i] > 85:
                tokens.remove(detected_table[2][i])    

        return detected_table[0]


    def indentify_col_tables(self, tokens, identified_table=None):
        res = dict()

        if not identified_table:
            identified_table = self.indentify_table(tokens)
            if not tokens:
                res[identified_table[0]] = ['*']
                return res
        else:
            identified_table = [identified_table]

        if identified_table:
            for table in identified_table:
                res[table] = dict()
                for token in tokens:
                    for column in self.db_schema[table].keys():
                        # for column in columns.keys():
                        if column=='pk' or column=='fk':
                            continue
                        else:
                            similarity = fuzz.ratio(token, column.lower())
                            if similarity >= 55:
                                if res[table].get(token):
                                    old_similarity = list(res[table][token].values())[0]
                                    if similarity > old_similarity:
                                        res[table][token] = {column: similarity}
                                else:
                                    res[table][token] = {column: similarity}


        else:
            for token in tokens:
                for table, columns in self.db_schema.items():
                    
                    cols = list(map(str.lower, list(columns.keys())))
                            
                    match = get_close_matches(token, cols)
                    if match:
                        if res.get(table):
                            res[table].add(match[0])
                        else:
                            res[table] = set(match)

        if identified_table:
            result = {}
            for table, token in res.items():
                cols = set()
                for col in token.values():
                    cols.update(col.keys())
                result[table] = cols

            result = {key: value for key, value in result.items() if value != set()}
            return result
        

        res = {key: value for key, value in res.items() if value != set()}    

        return res


    # JOIN
    def create_graph(self, directional=False):
        if directional:
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        # Add nodes and edges based on the SQL dictionary
        for table, details in self.db_schema.items():
            G.add_node(table)  # Add table as a node
            for fk_table in details['fk']:  # Iterate through foreign keys
                G.add_edge(table, fk_table)  # Create an edge from current table to foreign key table

        # Get nodes and edges for verification
        nodes = list(G.nodes)
        edges = list(G.edges)

        return G
    
    def required_tables_graph(self, G, start, end, required_tables):
        def dijkstra(graph, start, end):
            distances = {node: float('infinity') for node in graph}
            distances[start] = 0
            pq = [(0, start)]
            previous = {node: None for node in graph}

            while pq:
                current_distance, current_node = heapq.heappop(pq)

                if current_node == end:
                    path = []
                    while current_node:
                        path.append(current_node)
                        current_node = previous[current_node]
                    return path[::-1], current_distance

                for neighbor in graph[current_node]:
                    distance = current_distance + 1  # All edges have weight of 1
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current_node
                        heapq.heappush(pq, (distance, neighbor))

            return None, float('infinity')

        required_tables = set(required_tables) - {start, end}
        best_path = None
        best_distance = float('infinity')

        def dfs(current_path, current_distance, remaining_required):
            nonlocal best_path, best_distance

            if not remaining_required:
                path, distance = dijkstra(G, current_path[-1], end)
                if path:
                    total_path = current_path + path[1:]
                    total_distance = current_distance + distance
                    if total_distance < best_distance:
                        best_path = total_path
                        best_distance = total_distance
                return

            for node in remaining_required:
                path, distance = dijkstra(G, current_path[-1], node)
                if path:
                    new_path = current_path + path[1:]
                    new_distance = current_distance + distance
                    new_remaining = remaining_required - {node}
                    dfs(new_path, new_distance, new_remaining)

        dfs([start], 0, required_tables)

        return best_path, best_distance
    
    def graph_sort(self, edges):
        counts = Counter(t[0] for t in edges)
        
        # Sort tuples based on the counts in descending order
        sorted_tuples = sorted(edges, key=lambda x: counts[x[0]], reverse=True)
        
        return sorted_tuples

    def remove_duplicate_keys(self, edges):

        filtered_result = dict()

        for edge in edges:

            # Extract the keys from the dictionaries
            table0 = self.req_schema[edge[0]]
            table1 = self.req_schema[edge[1]]

            # Create a new dictionary with only the edge[0] key
            # and its value as the set of keys that are unique to edge[0]
            filtered_result[edge[0]]= table0 - table1
            if table1 - table0:
                filtered_result[edge[1]]= table1 - table0


            # If the result is an empty set, we want to keep the original edge[0] value
            if not filtered_result[edge[0]]:
                filtered_result[edge[0]] = self.req_schema[edge[0]]
        
        return filtered_result

    def join_clause(self):
        clause = ""

        # create graph from Database schema
        db_graph = self.create_graph()
        db_dir_graph = self.create_graph(directional=True)

        required_tables = list(self.req_schema.keys())

        min_dist = float('inf')
        for st_table in required_tables:
            for end_table in required_tables:
                sub_graph, distance = self.required_tables_graph(db_graph, st_table, end_table, required_tables)
                if distance < min_dist:
                    join_graph = OrderedSet(sub_graph)
                    min_dist = distance

        req_graph = []

        for edge in db_dir_graph.edges:
            # assumption binary relations between tables
            if edge[0] in join_graph and edge[1] in join_graph:
                req_graph.append(edge)

        req_graph = self.graph_sort(req_graph)

        self.req_schema = self.remove_duplicate_keys(req_graph)

        if len(self.req_schema) >1 :

            clause += f"{req_graph[0][0]}\n"

            for i, edge in enumerate(req_graph):
                table1 = edge[0]
                table2 = edge[1]
                fk_col = self.db_schema[table1]['fk'][table2] # foreign key corresponding to 2nd table  primary key
                pk_col = self.db_schema[table2]['pk'][0] # primary key of 2nd table
                clause += f"JOIN {table2} ON {table1}.{fk_col}={table2}.{pk_col} \n"

            self.query_template['FROM'] = clause
        else:
            clause += f"{req_graph[0][0]}\n"
            self.query_template['FROM'] = clause

        return clause

    def aggregate_parser(self, tokens):

        res = []
        i = 0
        thresh = 50
        pot_col = ""
        while i< len(tokens):
            if tokens[i].upper() in list(self.constants['aggregate_functions'].keys()):
                for table in self.db_schema.keys():
                    cols = list(self.db_schema[table].keys()) # to check with missing cols from prev functions
                    for col in cols:
                        if col not in ["pk", "fk"]:
                            similarity = fuzz.ratio(tokens[i+1], col)
                            if similarity > thresh:
                                thresh = similarity
                                pot_col = f"{table.lower()}.{col.lower()}"
                
                if pot_col:
                    res.append(f"{tokens[i].upper()}({pot_col})")
                    i += 2
            else:
                res.append(tokens[i])
                i+=1

        return res

    # CONDITION - WHERE & HAVING    
    def extract_conditions(self, tokens):
        """
        Extracts WHERE and HAVING conditions from a natural language query based on keywords 'where' and 'having',
        or based on comparison operators (=, >, <, <=, >=).

        Parameters:
        - input_query (str): The natural language query.
        - req_schema (dict): A dictionary containing table names as keys and list of column names as values.

        Returns:
        - dict: A dictionary with separate lists of WHERE and HAVING conditions, and aggregate functions.
        """

        tokens_copy = tokens.copy()
        # Define regex patterns for comparison operators and aggregate functions
        comparison_pattern = r'(=|>|<|>=|<=|!=)'  # To locate comparison operators

        # Initialize results
        where_conditions = []
        having_conditions = []

        # Split input query into tokens for easier parsing
        input_query = (' ').join(tokens_copy)

        # Detect keywords and their positions
        where_pos = input_query.lower().find("where")
        having_pos = input_query.lower().find("having")

        # Helper function to find nearest column and value around a comparison operator
        def find_column_and_value(tokens_copy, operator_index, req_schema):
            column = None
            value = None

            # Look before and after the operator for a column and a value
            if operator_index > 0:
                potential_column = tokens_copy[operator_index - 1]
                formatted_keys = [f'{column.lower()}' for table, columns in req_schema.items() for column in columns]
                match = get_close_matches(potential_column.lower(), formatted_keys)
                if match:
                    column = potential_column

            if operator_index < len(tokens_copy) - 1:
                potential_value = tokens_copy[operator_index + 1]
                # Check if it's a quoted value or a number
                if re.match(r"^'[^']*'$|^\d+(\.\d+)?$|^(?:\d{2}[/-]\d{2}[/-]\d{4})$", potential_value):
                    value = potential_value.strip("'").strip('"')

            return column, value

        res = self.aggregate_parser(tokens_copy)

        agg_flag = False

        for token in res:
            for agg in list(self.constants['aggregate_functions'].keys()):
                if agg.lower() in token.lower():
                    agg_flag = True

        for i, token in enumerate(res):
            if re.match(comparison_pattern, token):  # If it's a comparison operator
                column, value = find_column_and_value(res, i, self.req_schema)

                if column and value:
                    condition = {
                        "column": column,
                        "operator": token,
                        "value": value
                    }

                    # Check if the condition belongs to WHERE or HAVING based on position
                    if where_pos != -1 and having_pos == -1: # iff "where" in tokens
                        where_conditions.append(condition)
                    elif having_pos != -1 and where_pos == -1: # iff "where" in tokens
                        having_conditions.append(condition)
                    elif agg_flag and self.query_template['GROUP BY'] != -1: # iff "aggregate_function" in tokens
                        having_conditions.append(condition)
                    else: # default
                        where_conditions.append(condition)

        self.query_template['WHERE'] = where_conditions
        self.query_template['HAVING'] = having_conditions

        return res, {"where": where_conditions, "having": having_conditions}

    def indentify_order_by(self, tokens):
        result = []
        
        i = 0
        while i < len(tokens) - 1:
            if tokens[i].lower() == "order" and tokens[i+1].lower() == "by":
                for table, columns in self.req_schema.items():
                    match = get_close_matches(tokens[i+2], columns)
                    if match:
                        if "max" in tokens:
                            self.query_template["ORDER BY"] = f"{table}.{match[0]} DESC"
                            result.append(f"{tokens[i]} {tokens[i+1]} {table}.{match[0]} DESC")    
                        elif "descending" in tokens:
                            self.query_template["ORDER BY"] = f"{table}.{match[0]} DESC"
                            result.append(f"{tokens[i]} {tokens[i+1]} {table}.{match[0]} DESC")    
                        else:
                            self.query_template["ORDER BY"] = f"{table}.{match[0]}"
                            result.append(f"{tokens[i]} {tokens[i+1]} {table}.{match[0]}")
                i += 3
            else:
                result.append(tokens[i])
                i += 1
        if i < len(tokens):  # Add any remaining token
            result.extend(tokens[i:])

        return list(dict.fromkeys(result)) # removing duplicates
    
    # LIMIT
    def indentify_limit(self, tokens):
        limit = -1
        for i, token in enumerate(tokens):
            if token.lower() == "limit" or token.lower() == "limits":
                if tokens[i+1].isdigit():
                    limit = tokens[i+1]
                    self.query_template["LIMIT"] = tokens[i+1]
                    return
                else:
                    limit = 1
                    self.query_template["LIMIT"] = 1

        return limit


    

    def select_validator(self, tokens):
        # making sure all the required columns are present in select clause
        
        # check group by and having condition
        self.query_template['SELECT'] = ""
        select_cols = set()

        agg_funcs = list(self.constants['aggregate_functions'].keys())

        for token in tokens:
            for agg in agg_funcs:
                if agg in token:
                    select_cols.add(token)

        for table, cols in self.req_schema.items():
            for col in cols:
                full_col_name = f"{table}.{col}"
                should_add = True  # Flag to determine if we should add the column
                
                for sel_col in select_cols:
                    # Check if the normalized column (without DISTINCT()) matches
                    normalized_sel_col = re.sub(r"\w+\(", "", sel_col).replace(")", "")
                    
                    # If the normalized column matches the current table.column, skip adding
                    if full_col_name == normalized_sel_col:
                        should_add = False
                        break

                if should_add:
                    print(f"Adding {full_col_name}")
                    select_cols.add(full_col_name)



        group_by_col = self.query_template['GROUP BY']
        if group_by_col:
            for table, cols in self.req_schema.items():
                if group_by_col in cols:
                    select_cols.add(f"{table}.{group_by_col}")
                    self.query_template['GROUP BY'] = f"{table}.{group_by_col}"
                else:
                    if group_by_col in self.db_schema[table]:
                        match = get_close_matches(group_by_col, self.db_schema[table])
                        if match:
                            select_cols.add(f"{table}.{group_by_col}")
                            self.query_template['GROUP BY'] = f"{table}.{group_by_col}"

        
        having_col = self.query_template['HAVING']
        if group_by_col and having_col:
            for table, cols in self.req_schema.items():
                if group_by_col in cols:
                    select_cols.add(f"{table}.{group_by_col}")
        

        for cols in select_cols:
            self.query_template['SELECT']+=f"{cols}, "

        self.query_template['SELECT'] = self.query_template['SELECT'].strip(', ')

        return

    def query_template_generator(self, input, table) -> dict:

        # preprocess -> remove keywords -> group by -> columns & table identification 
        # -> join -> order by -> conditions -> where | having

        self.query_template = QUERY_TEMPLATE.copy()

        self.input = input

        self.tokens = self.preprocess_text(input)

        self.tokens_nk = self.remove_keywords(self.tokens)

        self.tokens_group = self.identify_group_by(self.tokens_nk)
    
        self.req_schema = self.indentify_col_tables(self.tokens_group, table)

        if len(self.req_schema)>1:
            self.from_clause = self.join_clause()
        
        else:
            for table in self.req_schema.keys():
                self.query_template['FROM'] = table

        self.agg_tokens, self.conditions = self.extract_conditions(self.tokens)

        self.order_by = self.indentify_order_by(self.tokens)
    
        self.limit = self.indentify_limit(self.tokens)

        self.select = self.select_validator(self.agg_tokens)

        return self.query_template