from pymongo import MongoClient

from src.chatdb.core.query_generator import QueryGenerator


class NoSQLGenerator(QueryGenerator):
    def __init__(self, db_schema, mongo_uri, db):
        super().__init__(db_schema)
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db]
        
    def psuedo_to_mongo_clause(self, sql_dict):
        """
        Converts a SQL-like dictionary to a MongoDB aggregation pipeline in dictionary format,
        including handling of joins using $lookup, aggregate functions, grouping, sorting, and projecting.

        Args:
            sql_dict (dict): SQL-like query dictionary.

        Returns:
            dict: MongoDB aggregation pipeline in dictionary format.
        """
        # Initialize MongoDB query components
        match = {}
        project = {}
        sort = {}
        group = None
        limit = None
        lookup = None
        unwind = None

        # Process JOIN in FROM clause
        from_clause = sql_dict.get('FROM', '')
        if 'JOIN' in from_clause:
            tables = from_clause.split('\nJOIN ')
            main_table = tables[0].strip()
            join_table_info = tables[1].split(' ON ')
            join_table = join_table_info[0].strip()
            join_condition = join_table_info[1].strip()

            left_key, right_key = join_condition.split('=')
            left_key = left_key.strip()
            right_key = right_key.strip()

            lookup = {
                "$lookup": {
                    "from": join_table,
                    "localField": left_key.split('.')[-1],
                    "foreignField": "_id",
                    "as": join_table
                }
            }
            unwind = {"$unwind": f"${join_table}"}
        else:
            main_table = from_clause

        # Process WHERE clause into $match
        where_clauses = sql_dict.get('WHERE', [])
        for condition in where_clauses:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']

            operator_map = {
                '=': '$eq', '>': '$gt', '<': '$lt',
                '>=': '$gte', '<=': '$lte', '<>': '$ne'
            }

            mongo_operator = operator_map.get(operator)
            if mongo_operator:
                match[column] = {mongo_operator: int(value) if value.isdigit() else value}

        # Handle SELECT clause for projection and aggregation
        select_clause = sql_dict.get('SELECT', '').split(', ')
        group_by = sql_dict.get('GROUP BY')
        
        if group_by != -1:  # If GROUP BY exists
            group = {"_id": {}}
            for col in group_by.split(', '):
                if col.strip():
                    field = col.strip().split('.')[-1]
                    print("group", field)
                    group["_id"][field] = f"${field}"

            for column in select_clause:
                column = column.strip()
                if '(' in column and ')' in column:  # Aggregate functions
                    func, field = column.split('(')
                    field = field.rstrip(')').split('.')[-1]
                    func = func.strip().upper()
                    if func in ['SUM', 'AVG', 'MAX', 'MIN']:
                        group[field] = {f"${func.lower()}": f"${field}"}
                    elif func == "COUNT":
                        group[field] = {f"${func.lower()}": {}}
                elif column not in group["_id"]:
                    field = column.split('.')[-1]
                    group[field] = {"$first": f"${field}"}
        else:  # No GROUP BY, use $project for selection and aggregation
            for column in select_clause:
                column = column.strip()
                if '(' in column and ')' in column:  # Aggregate functions
                    func, field = column.split('(')
                    field = field.rstrip(')').split('.')[-1]
                    func = func.strip().upper()
                    if func in ['SUM', 'AVG', 'MAX', 'MIN']:
                        project[field] = {f"${func.lower()}": f"${field}"}
                    elif func == "COUNT":
                        group[field] = {f"${func.lower()}": {}}
                else:
                    field = column.split('.')[-1]
                    project[field] = 1

        # Process ORDER BY
        order_by = sql_dict.get('ORDER BY', '')
        if order_by and order_by != -1:
            column, *direction = order_by.split(' ')
            direction = direction[0] if direction else 'ASC'
            sort[column.strip().split('.')[-1]] = -1 if direction.strip().upper() == 'DESC' else 1

        # Handle LIMIT
        limit = sql_dict.get('LIMIT')

        # Construct MongoDB query dictionary
        query_dict = {}
        pipeline = []
        if lookup:
            pipeline.append(lookup)
        if unwind:
            pipeline.append(unwind)
        # if match:
        pipeline.append({"$match": match})
        if group:
            pipeline.append({"$group": group})
        # if project:
        pipeline.append({"$project": project})
        if sort:
            pipeline.append({"$sort": sort})
        if limit and limit != -1:
            pipeline.append({"$limit": int(limit)})

        query_dict['pipeline'] = pipeline
        query_dict['collection'] = main_table

        return query_dict

    def mongod_parser(self, input, table=None):
        query_template = super().query_template_generator(input=input, table=table)

        print("query_template", query_template)
        pipeline = self.psuedo_to_mongo_clause(query_template)
        collection = pipeline['collection']
        pipeline = pipeline['pipeline']

        local_collection = self.db[collection]

        query = f"{collection}."
        group_flag = False
        for clause in pipeline:
            if "$group" in clause:
                group_flag = True

        print("pipeline", pipeline)
        if group_flag:
            print("in group")
            group_pipeline = []

            for stage in pipeline:
                stage_key = list(stage.keys())[0]
                if stage[stage_key]:  # Check if the stage's content is not empty
                    group_pipeline.append(stage)


            print("new_pipeline",group_pipeline)
            result = local_collection.aggregate(group_pipeline)
            query += f"aggregate({pipeline})"
        else:
            # sort, limit
            match_clause = {}
            project_clause = {}
            sort_clause = None
            limit_clause = None
            
            for clause in pipeline:
                if "$match" in clause:
                    match_clause = clause["$match"]
                if "$project" in clause:
                    print(clause["$project"])
                    project_clause = clause["$project"]
                if "$sort" in clause:
                    sort_clause = clause["$sort"]
                if "$limit" in clause:
                    limit_clause = clause["$limit"]

            print("here", match_clause, project_clause)
            if sort_clause and limit_clause:
                result = local_collection.find(match_clause, project_clause).sort(sort_clause).limit(limit_clause)
                query += f"find({match_clause}, {project_clause}).sort({sort_clause}).limit({limit_clause})"
            elif sort_clause:

                result = local_collection.find(match_clause, project_clause).sort(sort_clause)
                query += f"find({match_clause}, {project_clause}).sort({sort_clause})"
            elif limit_clause:
                result = local_collection.find(match_clause, project_clause).limit(limit_clause)
                query += f"find({match_clause}, {project_clause}).limit({limit_clause})"
            else:
                result = local_collection.find(match_clause, project_clause)
                query += f"find({match_clause}, {project_clause})"

        return query, list(result)
