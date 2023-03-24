from enum import Enum

# The basic language:

# Statement = Read | Write
# Read = "read" Register Address
# Write = "write" Address "=" Expression
# Term = Register | Const | Operator
# Operator = ("+"/"-"/"*") Term Term


class TermType(Enum):
    REGISTER = 1
    CONSTANT = 2
    OPERATOR = 3

class OperatorType(Enum):
    ADD = 1
    SUB = 2
    MUL = 3

    def __str__(self):
        if self == OperatorType.ADD:
            return "+"
        if self == OperatorType.SUB:
            return "-"
        if self == OperatorType.MUL:
            return "*"
        return "?"

class ReadWrite(Enum):
    READ = 1
    WRITE = 2

class Context:
    def __init__(self):
        self.registers = {}
        self.variables = {}

    def lookup_register(self, register):
        if register not in self.registers:
            return 0
        else:
            return self.registers[register]

    def lookup_variable(self, variable):
        if variable not in self.variables:
            return 0
        else:
            return self.variables[variable]

    def __repr__(self):
        for register in self.registers:
            print(f"r{register} = {self.registers[register]}")
        for variable in self.variables:
            print(f"X{variable} = {self.variables[variable]}")

class Term:
    def __init__(self, term_type, value, children=None):
        self.term_type = term_type
        self.value = value
        if term_type == TermType.OPERATOR:
            assert(type(children) == list)
            assert(type(value) == OperatorType)
        if children is None:
            self.children = []
        else:
            self.children = children

    def __repr__(self):
        if self.term_type == TermType.REGISTER:
            return f"r{self.value}"
        if self.term_type == TermType.CONSTANT:
            return f"{self.value}"
        if self.term_type == TermType.OPERATOR:
            return f"({self.children[0]} {self.value} {self.children[1]})"

    def __eq__(self, other):
        return self.term_type == other.term_type and self.value == other.value and self.children == other.children

    def registers(self) -> list[int]:
        if self.term_type == TermType.REGISTER:
            return [self.value]
        if self.term_type == TermType.CONSTANT:
            return []
        if self.term_type == TermType.OPERATOR:
            lhs = self.children[0].registers()
            rhs = self.children[1].registers()
            res = []
            for reg in lhs:
                if reg not in res:
                    res.append(reg)
            for reg in rhs:
                if reg not in res:
                    res.append(reg)
            return res

    def execute(self, context):
        if self.term_type == TermType.REGISTER:
            return context.lookup_register(self.value)
        if self.term_type == TermType.CONSTANT:
            return self.value
        if self.term_type == TermType.OPERATOR:
            lhs = self.children[0].execute(context)
            rhs = self.children[1].execute(context)
            if self.value == OperatorType.ADD:
                return lhs + rhs
            if self.value == OperatorType.SUB:
                return lhs - rhs
            if self.value == OperatorType.MUL:
                return lhs * rhs


class Statement:
    def __init__(self, readwrite : ReadWrite, lhs: int, rhs): # rhs : Term or int
        self.readwrite = readwrite
        if readwrite == ReadWrite.READ:
            if type(rhs) != int:
                raise Exception("Read statement must have variable on right hand side")
        elif readwrite == ReadWrite.WRITE:
            if type(rhs) != Term:
                raise Exception("Write statement must have term on right hand side")
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        if self.readwrite == ReadWrite.READ:
            return f"r{self.lhs} = X{self.rhs}"
        elif self.readwrite == ReadWrite.WRITE:
            return f"X{self.lhs} = {self.rhs}"

    def registers(self) -> list[int]:
        if self.readwrite == ReadWrite.READ:
            return [self.lhs]
        if self.readwrite == ReadWrite.WRITE:
            return self.rhs.registers()

    def variables(self) -> list[int]:
        if self.readwrite == ReadWrite.READ:
            return [self.rhs]
        elif self.readwrite == ReadWrite.WRITE:
            return [self.lhs]

    def execute(self,context): #mutate the context...
        if self.readwrite == ReadWrite.READ:
            context.registers[self.lhs] = context.lookup_variable(self.rhs)
        elif self.readwrite == ReadWrite.WRITE:
            rhs = self.rhs.execute(context)
            context.variables[self.lhs] = rhs


class AssertOperator(Enum):
    EQ = 1
    NEQ = 2
    LT = 3
    GT = 4
    def __repr__(self):
        if self == AssertOperator.EQ:
            return "=="
        if self == AssertOperator.NEQ:
            return "!="
        if self == AssertOperator.LT:
            return "<"
        if self == AssertOperator.GT:
            return ">"

class Assertion:
    def __init__(self, lhs: Term, rhs: Term, op: AssertOperator):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def __repr__(self):
        return f"{self.lhs} {self.op} {self.rhs}"

class Transaction:
    def __init__(self, statements : list[Statement]):
        self.statements = statements

    def __repr__(self):
        res = "Transaction:\n"
        for statement in self.statements:
            res += f"  {statement};\n"
        return res

    def registers(self) -> list[int]:
        res = []
        for statement in self.statements:
            for reg in statement.registers():
                if reg not in res:
                    res.append(reg)
        return res

    def variables(self) -> list[int]:
        res = []
        for statement in self.statements:
            for var in statement.variables():
                if var not in res:
                    res.append(var)
        return res

    def execute(self, context):
        for statement in self.statements:
            statement.execute(context)

