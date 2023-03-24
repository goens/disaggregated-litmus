#!/usr/bin/env python3

import random
from transactions import Term, TermType, OperatorType, Statement, ReadWrite, Transaction
from litmus import Litmus
from enum import Enum

# All binary operators for now
VALUES = list(range(0, 5))

def generate_expression(local_variables : int) -> Term:
    if local_variables == 0:
        weights = [0, 1, 0]
    else:
        weights = [0.5, 0.3, 0.2]
    term_type = random.choices(list(TermType), weights)[0]
    if term_type == TermType.REGISTER:
        idx =  random.choice(range(local_variables))
        return Term(term_type, idx)
    if term_type == TermType.CONSTANT:
        val = random.choice(VALUES)
        return Term(term_type, val)
    if term_type == TermType.OPERATOR:
        op = random.choice(list(OperatorType))
        lhs = generate_expression(local_variables)
        rhs = generate_expression(local_variables)
        return Term(term_type, op, [lhs, rhs])

def generate_read(local_variable : int, global_variables : int) -> Statement:
    var_idx = random.choice(range(global_variables))
    return Statement(ReadWrite.READ, local_variable, var_idx)

def generate_write(local_variables : int, global_variables : int) -> Statement:
    var_idx = random.choice(range(global_variables))
    return Statement(ReadWrite.WRITE, var_idx, generate_expression(local_variables))

def generate_transaction(num_variables : int, max_statements : int) -> Transaction:
    local = 0
    statements = []
    for _ in range(random.choice(range(1,max_statements))):
      if random.random() < 0.5: #Read
        statements.append(generate_read(local, num_variables))
        local += 1
      else: #Write
        statements.append(generate_write(local, num_variables))
    return Transaction(statements)

def generate_litmus(num_variables=3, num_transactions=2, max_statements=3) -> Litmus:
    transactions = []
    for t in range(num_transactions):
        transactions.append(generate_transaction(num_variables,max_statements))
    return Litmus(transactions)

if __name__ == "__main__":
    random.seed(0)
    for _ in range(100):
      litmus = generate_litmus()
      if litmus.assertion is not None:
          print(litmus)
          print("=================")
