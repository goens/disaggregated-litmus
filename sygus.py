import copy
import utils
import cvc5
from cvc5 import Kind


if __name__ == "__main__":
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
    x = slv.mkVar(integer, "x")
    y = slv.mkVar(integer, "y")

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
    grammar = slv.mkGrammar([x,y], [cond, term])

    # bind each non-terminal to its rules
    grammar.addRules(cond, [neg,conj,eq,leq])
    grammar.addRules(term, [x,y,const_i(0),const_i(1),const_i(2), ite])

    # add parameters as rules for the start symbol. Similar to "(Variable Int)"
    grammar.addAnyVariable(cond)

    # declare the functions-to-synthesize
    assertion = slv.synthFun("assertion", [x,y], boolean, grammar)


    # declare universal variables.
    varX = slv.declareSygusVar("x", integer)
    varY = slv.declareSygusVar("y", integer)

    # add positive constraints
    for i in range(1, 3):
        slv.addSygusConstraint(
              slv.mkTerm(Kind.APPLY_UF, assertion, slv.mkInteger(i), slv.mkInteger(i)))
    # negative constraints
    values = []
    for i in range(0, 3):
        for j in range(0, 3):
            values.append(slv.mkTerm(Kind.NOT,slv.mkTerm(Kind.APPLY_UF, assertion, slv.mkInteger(i), slv.mkInteger(j))))
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
