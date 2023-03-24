#!/usr/bin/env python3

from litmus import Transaction,Statement,ReadWrite,Term,TermType,OperatorType
import sygus

x = Term(TermType.REGISTER, 0)
y = Term(TermType.REGISTER, 1)
one = Term(TermType.CONSTANT, 1)
two = Term(TermType.CONSTANT, 2)


example_transaction1 = Transaction([Statement(ReadWrite.WRITE, 0, one),
                                    Statement(ReadWrite.WRITE, 1, one)])

example_transaction2 = Transaction([Statement(ReadWrite.WRITE, 0, two),
                                    Statement(ReadWrite.WRITE, 1, two)])

example_transaction3 = Transaction([Statement(ReadWrite.READ,  0, 0),
                                    Statement(ReadWrite.WRITE, 1, Term(TermType.OPERATOR, OperatorType.ADD, [x, one]))])

example_transaction4 = Transaction([Statement(ReadWrite.READ,  1, 1),
                                    Statement(ReadWrite.WRITE, 0, Term(TermType.OPERATOR, OperatorType.ADD, [y, one]))])

example_transaction5 = Transaction([Statement(ReadWrite.WRITE, 0, two)])


example_transaction6 = Transaction([Statement(ReadWrite.READ,  0, 0), # Read X
                                    Statement(ReadWrite.WRITE, 0, Term(TermType.OPERATOR, OperatorType.ADD, [x, one])),
                                    Statement(ReadWrite.WRITE, 1, Term(TermType.OPERATOR, OperatorType.ADD, [x, one]))])

example_transaction7 = Transaction([Statement(ReadWrite.READ,  0, 0), # Read X
                                    Statement(ReadWrite.WRITE, 0, Term(TermType.OPERATOR, OperatorType.ADD, [x, one])),
                                    Statement(ReadWrite.WRITE, 2, Term(TermType.OPERATOR, OperatorType.ADD, [x, one]))])

if __name__ == "__main__":
    print(example_transaction1)
    print(example_transaction2)
    sygus.find_assertion([example_transaction1, example_transaction2])
    print("=================================")

    print(example_transaction3)
    print(example_transaction4)
    sygus.find_assertion([example_transaction3, example_transaction4])
    print("=================================")

    print(example_transaction1)
    print(example_transaction5)
    sygus.find_assertion([example_transaction1, example_transaction5])
    print("=================================")

    print(example_transaction6)
    print(example_transaction7)
    sygus.find_assertion([example_transaction6, example_transaction7])
    print("=================================")
