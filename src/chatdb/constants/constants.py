stop_words = [
    'a', 'an', 'the',
    'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'we', 'our', 'ours', 'ourselves', 'they', 'them', 'their', 'theirs', 'themselves',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'do', 'does', 'did', 'have', 'has', 'had', 'can', 'could', 'shall', 'should', 'will', 'would', 'may', 'might', 'must',
    'about', 'across', 'after', 'against', 'along', 'around', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'during', 'into', 'near', 'off', 'out', 'through', 'toward', 'under', 'up', 'with',
    'if', 'then', 'because', 'as', 'until', 'while',
    'this', 'that', 'these', 'those', 'such', 'what', 'which', 'whose', 'whoever', 'whatever', 'whichever', 'whomever', 'either', 'neither', 'both',
    'very', 'really', 'always', 'never', 'too', 'already', 'often', 'sometimes', 'rarely', 'seldom', 'again', 'further', 'then', 'once', 'here', 'there', 'why', 'how',
    # 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'second', 'third', 'fourth', 'fifth', # find a way to implement it in limit
    'few', 'little', 'much', 'enough',
    'yes', 'no', 'not', 'okay', 'ok', 'right', 'sure', 'well', 'uh', 'um', 'oh', 'eh', 'hmm', 'just', 'ever', 'yet', 'etc', 'perhaps', 'maybe', 'list',
    'who', 'spent', 'of'
]

aggregate_functions = {
    'COUNT': ['count', 'number of', 'quantity of', 'total number of', 'tally', 'enumerate', 'how many'],
    'SUM': ['sum', 'total', 'aggregate', 'combined', 'add up', 'overall', 'cumulative'],
    'AVG': ['average', 'mean', 'typical', 'median', 'expected value', 'norm', 'central tendency'],
    'MAX': ['maximum', 'highest', 'most', 'top', 'peak', 'greatest', 'largest', 'biggest', 'uppermost', 'oldest'],
    'MIN': ['minimum', 'lowest', 'least', 'bottom', 'smallest', 'tiniest', 'least', 'floor', 'youngest'],
    'DISTINCT': ['unique', 'different', 'distinct', 'individual', 'separate', 'non-duplicate', 'exclusive'],
    # 'GROUP_CONCAT': ['concatenate', 'combine strings', 'join', 'merge text', 'string aggregation', 'text combination'],
    # 'FIRST': ['first', 'initial', 'earliest', 'primary', 'leading', 'opening', 'foremost'], # limit implementation along with number
    # 'LAST': ['last', 'final', 'latest', 'ultimate', 'concluding', 'terminal', 'closing']
}

comparison_operators = {
    '>': ['with greater than', 'greater than', 'with more than', 'more than', 'is above' ,'above', 'over', 'exceeding', 'surpassing', 'beyond', 'higher than', 'in excess of'],
    '<': ['with less than', 'less than', 'with fewer than', 'fewer than', 'is below' ,'below', 'under', 'beneath', 'lower than', 'not as much as', 'smaller than'],
    '=': ['equal to', 'is same as', 'same as', 'identical to', 'matching', 'equivalent to', 'corresponds to', 'is', 'assigned for', 'for', 'with'],
    '!=': ['not equal to', 'different from', 'excluding', 'not the same as', 'dissimilar to', 'unlike', 'other than'],
    '>=': ['greater than or equal to', 'at least', 'no less than', 'minimum of', 'not below', ' starting from'],
    '<=': ['less than or equal to', 'at most', 'no more than', 'maximum of', 'not above', 'up to'],
    'BETWEEN': ['between', 'in the range of', 'within the bounds of', 'inside the limits of'],
    'IN': ['in', 'within', 'among', 'included in', 'part of', 'contained in', 'one of'],
    'NOT IN': ['not in', 'outside of', 'excluded from', 'not among', 'not part of', 'not contained in'],
    'LIKE': ['like', 'similar to', 'resembling', 'matching pattern', 'corresponding to'],
    'NOT LIKE': ['not like', 'dissimilar to', 'unlike', 'not matching pattern', 'different from pattern']
}

logical_operators = {
    'AND': ['and', 'also', 'as well as', 'in addition to', 'plus', 'together with', 'along with', 'including'],
    'OR': ['or', 'alternatively', 'either', 'otherwise', 'else', 'and/or'],
    'NOT': ['not', 'except', 'excluding', 'other than', 'but not', 'save for', 'apart from']
}

data_types = {
    'INTEGER': ['integer', 'int', 'whole number', 'numeric'],
    'FLOAT': ['float', 'decimal', 'real number', 'fractional number'],
    'VARCHAR': ['string', 'text', 'characters', 'alphanumeric'],
    'DATE': ['date', 'calendar day', 'day'],
    'TIMESTAMP': ['timestamp', 'date and time', 'moment', 'point in time'],
    'BOOLEAN': ['boolean', 'true/false', 'yes/no', 'binary']
}

# order matters
sql_clauses = {
    'FROM': ['from', 'in', 'out of', 'sourced from', 'derived from', 'based on'],
    'WHERE': ['where', 'for which', 'that have', 'meeting the condition', 'satisfying', 'fulfilling'],
    'ORDER BY': ['order by', 'ordered by', 'sort by', 'sorted by', 'arrange by', 'rank by', 'sequence by'],
    'GROUP BY': ['group by', 'grouped by', 'categorize by', 'classify by', 'organize by', 'arrange by', 'cluster by', 'for each', 'broken down by', 'per', 'by'], # check about 'by'
    'HAVING': ['having', 'with the condition', 'subject to', 'meeting the criteria', 'have'],
    'LIMIT': ['limit', 'top', 'first', 'restrict to', 'cap at', 'only show'],
    'JOIN': ['join', 'combine', 'merge', 'connect', 'link', 'associate'],
    'UNION': ['union', 'combine', 'merge', 'incorporate', 'consolidate', 'unite'],
    'INTERSECT': ['intersect', 'in common', 'shared by', 'mutual', 'overlapping'],
    'EXCEPT': ['except', 'subtract', 'exclude', 'remove', 'omit', 'leave out'],
    'SELECT': ['show', 'list all', 'list', 'give', 'return', 'fetch', 'retrieve', 'get', 'find', 'which', 'what is the', 'what is', 'what are', 'what'], # 'display
}

ALL_KEYWORDS = set(list(aggregate_functions.keys())) | (set(list(logical_operators.keys()))) | (set(sql_clauses.keys())) | (set(comparison_operators.keys()))
ALL_KEYWORDS = list(map(str.lower, ALL_KEYWORDS))

CONSTANTS = {"ALL_KEYWORDS": ALL_KEYWORDS,
             "sql_clauses": sql_clauses,
             "data_types": data_types,
             "logical_operators": logical_operators,
             "comparison_operators": comparison_operators,
             "aggregate_functions": aggregate_functions,
             "stop_words": stop_words}

QUERY_TEMPLATE = {
    "SELECT": "",
    "FROM": -1,
    "WHERE": [], 
    'HAVING': [],
    "GROUP BY": -1,
    "ORDER BY": -1,
    "LIMIT": -1
}