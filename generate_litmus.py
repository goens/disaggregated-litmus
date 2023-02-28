#!/usr/bin/env python3

import random
from enum import Enum

class Term(Enum):
    VARIABLE = 1
    CONSTANT = 2
    OPERATOR = 3

# All binary operators for now
OPERATORS = ["+", "-", "*"]
VALUES = list(range(0, 5))

def generate_expression(local_variables : int) -> str:
    if local_variables == 0:
        weights = [0, 1, 0]
    else:
        weights = [0.5, 0.3, 0.2]
    term_type = random.choices(list(Term), weights)[0]
    if term_type == Term.VARIABLE:
        idx =  random.choice(range(local_variables))
        return f"r{idx}"
    elif term_type == Term.CONSTANT:
        val = (random.choice(VALUES))
        return str(val)
    elif term_type == Term.OPERATOR:
        op = random.choice(OPERATORS)
        lhs = generate_expression(local_variables)
        rhs = generate_expression(local_variables)
        # TODO: Here we could add parenthesis only when needed
        return f"( {lhs} {op} {rhs})"
    else:
        raise Exception(f"Invalid term type {term_type}")

def generate_read(local_variable : int, global_variables : int) -> str:
    var_idx = random.choice(range(global_variables))
    return f"r{local_variable} = X{var_idx}"

def generate_write(local_variables : int, global_variables : int) -> str:
    var_idx = random.choice(range(global_variables))
    return f"X{var_idx} = {generate_expression(local_variables)}"

def generate_transaction(num_variables : int, max_statements : int) -> str:
    res = ""
    local = 0
    for _ in range(random.choice(range(1,max_statements))):
      if random.random() < 0.5: #Read
        res += f"  {generate_read(local, num_variables)}\n"
        local += 1
      else: #Write
        res += f"  {generate_write(local, num_variables)}\n"
    return res

def generate_litmus(num_variables=3, num_transactions=2, max_statements=3) -> str:
    res = ""
    for t in range(num_transactions):
        res += f"T{t}:\n"
        res += generate_transaction(num_variables,max_statements)
    return res


if __name__ == "__main__":
    random.seed(0)
    for _ in range(10):
      print(generate_litmus())
