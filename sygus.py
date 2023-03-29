import copy
import cvc5
import transactions as ts
from examples import example_transaction1, example_transaction2, example_transaction3, example_transaction4
import itertools
from copy import deepcopy
from cvc5 import Kind

MAX_CONST = 2
MAX_STATES = 10

def define_fun_to_string(f, body):
    assert(f.getSort().isFunction())
    assert(f.getSort().getFunctionCodomainSort().isBoolean())
    result += ") " + str(sort) + " " + str(body) + ")"
    return result

def get_synth_solutions(terms, sols):
    for i in range(0, len(terms)):
        params = []
        body = sols[i]
        if sols[i].getKind() == Kind.LAMBDA:
            if sols[i].getSort().getFunctionCodomainSort().isBoolean():
                return(str(sols[i][1]))
    return None

def find_assertion(transactions : list[ts.Transaction]):
    slv = cvc5.Solver()
    # required options
    slv.setOption("sygus", "true")
    slv.setOption("incremental", "false")
    slv.setOption("tlimit", "10000")
    slv.setOption("rlimit", "10000")
    slv.setLogic("LIA")
    integer = slv.getIntegerSort()
    boolean = slv.getBooleanSort()


    # Grammar for the invariants
    # Something like the example for Alur et al. FMCAD'13
    # Term := x1 | ... | xn | Const | ITE(Cond, Term, Term)
    # Cond := Term <= Term | Cond && Cond | ! Cond | (Cond)

    # declare input variables for the function-to-synthesize
    variable_idxs = []
    for transaction in transactions:
        for variable in transaction.variables():
            if variable not in variable_idxs:
                variable_idxs.append(variable)

    register_idxs = []
    for transaction in transactions:
        for register in transaction.registers():
            if register not in register_idxs:
                register_idxs.append(register)

    variables = [ slv.mkVar(integer, f"X{i}") for i in variable_idxs ]

    # declare the grammar
    cond = slv.mkVar(boolean, "Cond")
    term = slv.mkVar(integer, "Term")
    def const_i(i : int):
        return slv.mkInteger(i)

    # define the rules
    ite = slv.mkTerm(Kind.ITE, cond, term, term)
    eq = slv.mkTerm(Kind.EQUAL, term, term)
    leq = slv.mkTerm(Kind.LEQ, term, term)
    neg = slv.mkTerm(Kind.NOT, cond)
    conj = slv.mkTerm(Kind.AND, cond, cond)

    # create the grammar object
    grammar = slv.mkGrammar(variables, [cond, term])

    # bind each non-terminal to its rules
    grammar.addRules(cond, [neg,conj,eq,leq])
    grammar.addRules(term, [*variables,*[const_i(i) for i in range(1, MAX_CONST + 1)], ite])

    # add parameters as rules for the start symbol. Similar to "(Variable Int)"
    grammar.addAnyVariable(cond)

    # declare the functions-to-synthesize
    assertion = slv.synthFun("assertion", variables, boolean, grammar)

    # add positive constraints
    # initialize with empty context
    #ypositive_constraints = [[0]*len(variable_idxs)]
    positive_constraints = []
    contexts = [ts.Context()]
    seen = []
    iters = 0
    while len(contexts) > 0 and iters < MAX_STATES:
        iters += 1
        context = contexts.pop()
        seen.append(context)
        for transaction in transactions:
            # mutate context
            new_context = deepcopy(context)
            transaction.execute(new_context)
            if new_context not in seen:
                contexts = [new_context] + contexts
            variable_values = [new_context.lookup_variable(variable) for variable in variable_idxs]
            if variable_values not in positive_constraints:
                positive_constraints.append(variable_values)
                values_cvc5 = list(map(slv.mkInteger, variable_values))
                #print(f"Adding positive constraint: {variable_values}")
                slv.addSygusConstraint(slv.mkTerm(Kind.APPLY_UF, assertion, *values_cvc5))

    # negative constraints
    statements = itertools.chain.from_iterable([ t.statements for t in transactions ])
    values = []
    negative_constraints = []
    contexts = [ts.Context()]
    seen = []
    iters = 0

    while len(contexts) > 0 and iters < MAX_STATES:
        iters += 1
        context = contexts.pop()
        for statement in statements:
            # mutate context
            new_context = deepcopy(context)
            statement.execute(new_context)
            if new_context not in seen:
                contexts = [new_context] + contexts
            variable_values = [new_context.lookup_variable(variable) for variable in variable_idxs]
            if variable_values not in negative_constraints and variable_values not in positive_constraints:
                negative_constraints.append(variable_values)
                #print(f"Adding negative constraint: {variable_values}")
                values_cvc5 = list(map(slv.mkInteger, variable_values))
                values.append(slv.mkTerm(Kind.NOT,slv.mkTerm(Kind.APPLY_UF, assertion, *values_cvc5)))
    if len(values) == 0:
        return None # No negative constraints; Can't disambiguate with an assertion.
    elif len(values) == 1:
        slv.addSygusConstraint(values[0])
    else:
        slv.addSygusConstraint(slv.mkTerm(Kind.OR, *values))

    if (slv.checkSynth().hasSolution()):
        terms = [assertion]
        return get_synth_solutions(terms, slv.getSynthSolutions(terms))
