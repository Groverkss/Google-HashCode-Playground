import argparse

input_file = "./input/e.in"
solution_file = "./output/e_out.out"


def ni(itr):
    return int(next(itr))


# parses the next string of itr as a list of integers
def nl(itr):
    return [int(v) for v in next(itr).split()]


class Compilable:
    def __init__(self, i, name, c, r, deps, ns):
        self.i = i
        self.name = name
        self.c = c
        self.r = r
        self.orig_deps = set(deps)
        self.deps = set(deps)
        for d in deps:
            self.deps |= ns.compilable[d].deps


class Target:
    def __init__(self, i, name, d, g):
        self.name = name
        self.d = d
        self.g = g
        self.i = i

    def get_comp(self, ns):
        return ns.compilable[ns.name2id[self.name]]


def parse(inp):
    itr = (line for line in inp.split("\n"))
    ns = argparse.Namespace()
    ns.C, ns.T, ns.S = nl(itr)
    ns.compilable = []
    ns.name2id = {}
    for i in range(ns.C):
        name, c, r = next(itr).split()
        ns.name2id[name] = i
        deps = [ns.name2id[n] for n in next(itr).split()[1:]]
        ns.compilable.append(Compilable(i, name, int(c), int(r), deps, ns))
    ns.targets = []
    for i in range(ns.T):
        name, d, g = next(itr).split()
        ns.targets.append(Target(i, name, int(d), int(g)))

    ns.avil = {}

    return ns


class Server:
    def __init__(self, i):
        self.t = 0
        self.compiled = set()
        self.id = i

    def add_compilation(self, i, ns):
        ok = True
        start = self.t
        File = ns.compilable[i]
        for dep in File.deps:
            if dep in self.compiled:
                continue
            else:
                assert dep in ns.avil, "file {} not ready".format(dep)
                start = max(start, ns.avil[dep])
        self.compiled.add(i)
        self.t = start + File.c
        if i in ns.avil:
            ns.avil[i] = min(ns.avil[i], self.t + File.r)
        else:
            ns.avil[i] = self.t + File.r


# inp: the input file as a single string
# out: the answer file produced by your solver, as a single string
# return the score of the output as an integer
def score(inp, out):
    ns = parse(inp)
    itr = (line for line in out.split("\n"))
    Srvs = [Server(i) for i in range(ns.S)]
    E = ni(itr)
    for _ in range(E):
        name, s_id = next(itr).split()
        s_id = int(s_id)
        f_id = ns.name2id[name]
        Srvs[s_id].add_compilation(f_id, ns)
    tot = 0
    picked = []
    goal, speed = 0, 0
    for targ in ns.targets:
        targ_id = ns.name2id[targ.name]
        if targ_id in ns.avil:
            time = ns.avil[targ_id] - ns.compilable[targ_id].r
            if time <= targ.d:
                goal += targ.g
                speed += targ.d - time
                tot += targ.g - time + targ.d
                picked.append(targ.d)
    print("Number of targets picked {}".format(len(picked)))
    print("Goal Score:", goal, "Speed Score:", speed)
    return tot


with open(input_file) as inpf, open(solution_file) as outf:
    inp = inpf.read()
    out = outf.read()
    print("Total Score:", score(inp, out))
