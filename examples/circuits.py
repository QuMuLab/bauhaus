
from pprint import pprint
import time

from nnf import Var, And, Or, true, false, all_models, config, dimacs, Aux
from nnf.operators import iff


FORCE_TREE = True
e = Encoding()

@proposition(e)
class Gate:
    def __init__(self, ID):
        self.ID = ID

    def __str__(self):
        return "Gate(%d)" % self.ID

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

@proposition(e)
class GateType:
    def __init__(self, gatevar, modality):
        self.gatevar = gatevar
        self.modality = modality

    def __str__(self):
        modalities = {'and': '∧', 'or': '∨', 'not': '¬'}
        return "%s(%d)" % ([self.modality], self.gatevar.name.ID)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

@proposition(e)
class Connection:
    symbol = "->"
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return "%s %s %s" % (str(self.src), self.symbol, str(self.dst))

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

@proposition(e)
class Order(Connection):
    symbol = ">"


def unique(lst):
    return len(set(lst)) == len(lst)

def model_to_bitvec(m, vars):
    return ''.join([{True:'1',False:'0'}[m[v.name]] for v in vars])

def model_to_varclone(m, vars, var):
    return "%s(%s)" % (str(var), model_to_bitvec(m, vars))

def clone_varset(models, model_vars, varset):
    clones = {}
    for m in models:
        bitvec = model_to_bitvec(m, model_vars)
        clones[bitvec] = {}
        for v in varset:
            clones[bitvec][v] = Var(model_to_varclone(m, model_vars, v))
    return clones


# models should either be the full 2^n models, or []. If the latter, then we
#  assume that the theory is being built for model counting after projecting to
#  the set of vars in the input theory. If the count < 2^n, then no circuit can
#  capture the full function.
def encode_circuit_search(original_theory, num_gates, models=[]):

    ########
    # Vars #
    ########

    # Inputs to the circuit are the variables of the input theory
    inputs = [Var(v) for v in original_theory.vars()]
    if models:
        input_clones = clone_varset(models, inputs, inputs)
    else:
        input_clones = {}

    # Gates are either & | or ~
    gates = []
    gate_modalities = {}
    for i in range(num_gates):
        gates.append(Var(Gate(i)))
        gate_modalities[gates[-1]] = {}
        for m in ['and', 'or', 'not']:
            gate_modalities[gates[-1]][m] = Var(GateType(gates[-1], m))

    if models:
        gate_clones = clone_varset(models, inputs, gates)
    else:
        gate_clones = {}

    # Single (arbitrary) gate is the circuit output
    output = gates[0]

    # Connections between inputs/gates to gates, and transitivity
    connections = {}
    unconnections = {}
    for src in inputs + gates[1:]:
        connections[src] = {}
        for dst in gates:
            if src != dst:
                connections[src][dst] = Var(Connection(src, dst))
                if dst not in unconnections:
                    unconnections[dst] = {}
                unconnections[dst][src] = connections[src][dst]
    C = connections # convenience

    orders = {}
    for src in gates:
        orders[src] = {}
        for dst in gates:
            orders[src][dst] = Var(Order(src,dst))



    ###############
    # Constraints #
    ###############

    ''' add decorators for simplifying adding constraints (i.e. a conjunct)'''
    conjuncts = []

    # Orderings (to forbid cycles in the circuit)
    for g1 in gates:
        # Connection implies orders
        for src in connections:
            for dst in connections[src]:
                if isinstance(src.name, Gate) and isinstance(dst.name, Gate):
                    conjuncts.append(~connections[src][dst] | orders[src][dst])
        # Can't order before yourself
        conjuncts.append(~orders[g1][g1])
        # Transitive closure
        for g2 in gates:
            for g3 in gates:
                conjuncts.append(~orders[g1][g2] | ~orders[g2][g3] | orders[g1][g3])

    if FORCE_TREE:
        # At max one outgoing connection on a gate
        for src in gates[1:]:
            for dst1 in connections[src]:
                for dst2 in connections[src]:
                    if dst1 != dst2:
                        conjuncts.append(~connections[src][dst1] | ~connections[src][dst2])

    # Every gate has at least one input
    for dst in unconnections:
        conjuncts.append(Or(unconnections[dst].values()))

    # Every gate has at most two inputs and negation gates have at most one
    for j in gates:
        for i1 in inputs+gates[1:]:
            for i2 in inputs+gates[1:]:
                if not unique([j,i1,i2]):
                    continue
                conjuncts.append(~gate_modalities[j]['not'] | ~C[i1][j] | ~C[i2][j])
                for i3 in inputs+gates[1:]:
                    if not unique([j,i1,i2,i3]):
                        continue
                    conjuncts.append(~C[i1][j] | ~C[i2][j] | ~C[i3][j])

    # Every gate has exactly one modality
    for g in gates:
        # At least one
        conjuncts.append(Or(gate_modalities[g].values()))

        # At most one
        for m1 in ['and', 'or', 'not']:
            remaining = set(['and', 'or', 'not']) - set([m1])
            conjuncts.append(Or([~gate_modalities[g][m2] for m2 in remaining]))

    # Re-usable theories
    notneg_cache = {}
    def notneg(src, dst, cloned_src=None):
        if not cloned_src:
            cloned_src = src
        if (cloned_src,dst) not in notneg_cache:
            notneg_cache[(cloned_src,dst)] = ~C[src][dst] | cloned_src
        return notneg_cache[(cloned_src,dst)]

    notpos_cache = {}
    def notpos(src, dst, cloned_src=None):
        if not cloned_src:
            cloned_src = src
        if (cloned_src,dst) not in notpos_cache:
            notpos_cache[(cloned_src,dst)] = ~C[src][dst] | ~cloned_src
        return notpos_cache[(cloned_src,dst)]

    # Implement the gates
    for g in gates:

        ins = [i for i in inputs+gates[1:] if i != g]

        conjuncts.append(~gate_modalities[g]['and'] | iff(g, And([notneg(src,g) for src in ins])))

        t = Or([notpos(src,g).negate() for src in ins])
        conjuncts.append(~gate_modalities[g]['or'] | iff(g, t))

        conjuncts.append(~gate_modalities[g]['not'] | iff(g, t.negate()))

        for m in models:
            bitvec = model_to_bitvec(m, inputs)
            orig_mapping = {**{input_clones[bitvec][i]: i for i in inputs if i != g},
                            **{gate_clones[bitvec][i]: i for i in gates[1:] if i != g}}
            ins = orig_mapping.keys()

            conjuncts.append(~gate_modalities[g]['and'] | iff(gate_clones[bitvec][g],
                     And([notneg(orig_mapping[src],g,src) for src in ins])))

            t = Or([notpos(orig_mapping[src],g,src).negate() for src in ins])
            conjuncts.append(~gate_modalities[g]['or'] | iff(gate_clones[bitvec][g], t))

            conjuncts.append(~gate_modalities[g]['not'] | iff(gate_clones[bitvec][g], t.negate()))


    # Finally, lock in the models
    if models:
        for m in models:
            bitvec = model_to_bitvec(m, inputs)
            for var in m:
                if m[var]:
                    conjuncts.append(input_clones[bitvec][Var(var)])
                else:
                    conjuncts.append(~input_clones[bitvec][Var(var)])
            if original_theory.satisfied_by(m):
                conjuncts.append(gate_clones[bitvec][output])
            else:
                conjuncts.append(~gate_clones[bitvec][output])
    else:
        for model in all_models(original_theory.vars()):

            t = false # negating the conjunction because of the implication: flips the signs
            for var,val in model.items():
                if val:
                    t |= ~Var(var)
                else:
                    t |= Var(var)
            if original_theory.satisfied_by(model):
                t |= output
            else:
                t |= ~output
            conjuncts.append(t)


    versions = {}
    example = {}
    for c in conjuncts:
        cn = c.simplify().to_CNF()
        stats = "(%d / %d / %d) > (%d / %d / %d)" % (c.simplify().size(), c.simplify().height(), len(c.simplify().vars()),
                                                     cn.size(), cn.height(), len(cn.vars()))
        example[stats] = str(c.simplify())
        versions[stats] = versions.get(stats, 0) + 1
    print("Conjunct stats:")
    for k in versions:
        print("\n - (%d) %s: %s" % (versions[k], k, example[k]))

    T = And(conjuncts)
    return T.simplify(), inputs, gates, output, connections, unconnections, gate_modalities


def build_solution(inputs, gates, gate_modalities, model, output, unconnections, nnf_syntax=False):

    if not isinstance(output.name, Gate):
        return str(output)

    children = []
    for child in unconnections[output]:
        if model[unconnections[output][child].name]:
            children.append(build_solution(inputs, gates, gate_modalities, model, child, unconnections, nnf_syntax))

    if model[gate_modalities[output]['not'].name]:
        assert len(children) == 1
        if nnf_syntax:
            return "%s.negate()" % str(children[0])
        else:
            return "¬%s" % str(children[0])
    if model[gate_modalities[output]['and'].name]:
        assert len(children) <= 2
        if nnf_syntax:
            return '('+ ' & '.join(children) + ')'
        else:
            return '('+ ' ∧ '.join(children) + ')'
    if model[gate_modalities[output]['or'].name]:
        assert len(children) <= 2
        if nnf_syntax:
            return '('+ ' | '.join(children) + ')'
        else:
            return '('+ ' ∨ '.join(children) + ')'
    assert False, "Huh?"


def solve_and_output(theory, bound):
    encoded, inputs, gates, output, connections, unconnections, gate_modalities = encode_circuit_search(theory, bound, list(all_models(theory.vars())))
    print("  Size: %d" % encoded.size())
    print("Height: %d" % encoded.height())
    print("  Vars: %d" % len(encoded.vars()))
    with open('encoded.cnf', 'w') as f:
        th = encoded.to_CNF()
        print("Compiled Vars: %d" % len(th.vars()))
        print("Compiled Clauses: %d" % len(th.children))
        print ("AxVars: %d" % len(list(filter(lambda x: isinstance(x, Aux), th.vars()))))
        var_labels = dict(enumerate(th.vars(), start=1))
        var_labels_inverse = {v: k for k, v in var_labels.items()}
        dimacs.dump(th, f, mode='cnf', var_labels=var_labels_inverse)

    with config(sat_backend="kissat"):
        t0 = time.time()
        model = encoded.solve()
        print("\nSolver complete in %.2fsec" % (time.time()-t0))
        if not model:
            print("No solution for bound %d\n" % bound)
            return

    print("\nGates:")
    for var in model:
        if isinstance(var, GateType) and model[var]:
            print(var)
    print("\nConnections:")
    for var in model:
        if isinstance(var, Connection) and model[var]:
            print(var)
    print("\nOutput: %s" % output)

    print("\nConfig for 1110:")
    for var in model:
        if '1110' in str(var):
            print("%s: %s" % (str(var), str(model[var])))

    print("\n  %s" % build_solution(inputs, gates, gate_modalities, model, output, unconnections))

    print()


w,x,y,z = map(Var, 'wxyz')

# 19 should be the smallest possible
#
theory = (((((w | z).negate()) | (w & z)) & (x & y)) | (((x | (w | y)).negate()) | (((w | z) & (x | y)) & (((w & z) | (x & y)).negate()))))



# theory = (w & x).negate() | (y & z)

solve_and_output(theory, 19)

# for i in range(19,20):
#     solve_and_output(theory, i)