import copy
import utils
import cvc5
import litmus
import itertools
from cvc5 import Kind

MAX_CONST = 2

def find_assertion(transactions : list[litmus.Transaction]) -> litmus.Litmus:
    slv = cvc5.Solver()
    # required options
    slv.setOption("sygus", "true")
    slv.setOption("incremental", "false")
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

    variables = [ slv.mkVar(integer, f"x{i}") for i in variable_idxs ]

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
    for p in itertools.permutations(transactions):
        context = litmus.Context()
        for transaction in p:
            # mutate context
            transaction.execute(context)
        variable_values = [context.lookup_variable(variable) for variable in variable_idxs]
        values_cvc5 = list(map(slv.mkInteger, variable_values))
        slv.addSygusConstraint(slv.mkTerm(Kind.APPLY_UF, assertion, *values_cvc5))
    # negative constraints
    statements = itertools.chain.from_iterable([ t.statements for t in transactions ])
    values = []
    for p in itertools.permutations(statements):
        context = litmus.Context()
        for statement in p:
            # mutate context
            statement.execute(context)
        varible_values = [slv.mkInteger(context.lookup_variable(variable)) for variable in variable_idxs]
        values.append(slv.mkTerm(Kind.NOT,slv.mkTerm(Kind.APPLY_UF, assertion, *varible_values)))
    slv.addSygusConstraint(slv.mkTerm(Kind.OR, *values))

    # print solutions if available

    if (slv.checkSynth().hasSolution()):

      # Output should be equivalent to:
      # (define-fun id1 ((x Int)) Int (+ x (+ x (- x))))
      # (define-fun id2 ((x Int)) Int x)
      # (define-fun id3 ((x Int)) Int (+ x 0))
      # (define-fun id4 ((x Int)) Int (+ x (+ x (- x))))
      terms = [assertion]
      utils.print_synth_solutions(terms, slv.getSynthSolutions(terms))

if __name__ == "__main__":
    find_assertion([litmus.example_transaction1, litmus.example_transaction2])
