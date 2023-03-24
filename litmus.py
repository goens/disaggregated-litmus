from transactions import *
import sygus


class Litmus:
    def __init__(self, transactions : list[Transaction], assertion=None):
        self.transactions = transactions
        if assertion is None:
            self.assertion = sygus.find_assertion(transactions)
        else:
            self.assertion = assertion

    def __repr__(self):
        res = ""
        for i,transaction in enumerate(self.transactions):
            res += f"T{i}:\n"
            res += f"{transaction}\n"
        res += f"assert({self.assertion});"
        return res
