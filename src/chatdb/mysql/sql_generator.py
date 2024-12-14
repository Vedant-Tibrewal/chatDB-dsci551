from src.chatdb.core.query_generator import QueryGenerator
import re


class SQLGenerator(QueryGenerator):
    def __init__(self, db_schema):
        super().__init__(db_schema)
    
    def sql_parser(self, input, table):
        query_template = super().query_template_generator(input, table=table)

        query = ""

        for key, values in query_template.items():
            if query_template[key] != -1 and query_template[key]:
                if key=="FROM":
                    query += f"{key.upper()} {values}\n"
                    query = re.sub(r'\n\n', r'\n', query)
                elif key!="WHERE" and key != "HAVING":
                    query += f"{key.upper()} {values}\n"
                else:
                    # specifc to Condition clause
                    for cond in query_template[key]:
                        condition = list(cond.values())
                        if condition[-1].isalpha():
                            query += f"{key} {condition[0]} {condition[1]} '{condition[2]}' AND"
                        else:
                            query += f"{key} {condition[0]} {condition[1]} {condition[2]} AND"

                    
                    query = query[:-3] # removing extra AND
                    query +=  "\n"

        query = query.strip()
        query += ";"

        return query
