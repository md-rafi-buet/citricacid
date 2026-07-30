import networkx as nx
import uuid
from itertools import chain, combinations
from typing import Union

def isempty(s: set) -> bool:
    """
    Checks if a given set is empty. Works for any iterable.
    """
    return len(s) == 0

def powerset(iterable: set) -> set[frozenset]:
    """
    Generates the powerset of the given iterable excluding the empty set. 
    Each element of the powerset is represented as a frozenset.
    """
    s = list(iterable)
    iterator = chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))
    return set(map(lambda x: frozenset(x), iterator))

class Material:
    """
    Material object representing a material in the P-graph.
    """
    def __init__(self, name: str, properties: dict=None):
        self.uuid = f"m_{uuid.uuid4()}"
        self.name = name
        self.properties = properties if properties else {}

    def __add__(self, other):
        if not isinstance(other, Material):
            return NotImplemented
        return Stream(self, other)

    def __repr__(self):
        return f"Material(name={self.name})"

    def __str__(self):
        return f"{self.name}"

    # CRITICAL FIX: Allow Materials to be evaluated correctly in sets
    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        return isinstance(other, Material) and self.uuid == other.uuid

class Stream:
    """
    Represents a combination of materials moving together.
    """
    def __init__(self, *args: Material):
        self.materials = list(args)

    def __add__(self, other: Material):
        self.materials.append(other)
        return self

    def __str__(self):
        return ", ".join({material.name for material in self.materials})

class Basis:
    def __init__(self, quantity: float, unit: str):
        self.unit = unit
        self.quantity = quantity

class Impacts:
    def __init__(self, basis: Basis = None, gwp: float = None, ap: float = None,
                 ep: float = None, htp: float = None, 
                 properties: dict = {'impact_assessment_method': 'CML v4.8 2016'}):
        self.gwp = gwp # kg CO2 eq
        self.ap = ap # kg SO2 eq
        self.ep = ep # kg PO4 eq
        self.htp = htp # kg 1,4-DB eq
        self.basis = basis
        self.properties = properties

class Operation:
    """
    An operation converts a set of Material objects (`m_in`) into another set
    of Material objects (`m_out`).
    """
    def __init__(self, name: str, m_in: set[Union[Material, Stream]], 
                 m_out: set[Union[Material, Stream]], impacts: Impacts = None, 
                 properties: dict=None):
        self.uuid = f"o_{uuid.uuid4()}"
        self.name = name
        self.impacts = impacts if impacts else Impacts()
        self.properties = properties if properties else {}

        # CRITICAL FIX: Unpack Streams into standalone Materials
        self.m_in = self._unpack(m_in)
        self.m_out = self._unpack(m_out)

    def _unpack(self, items):
        unpacked = set()
        for item in items:
            if isinstance(item, Stream):
                unpacked.update(item.materials)
            elif isinstance(item, Material):
                unpacked.add(item)
        return unpacked

    def __repr__(self):
        return f"Operation(name={self.name})"

    def __str__(self):
        return f"{self.name}"

    # CRITICAL FIX: Allow Operations to be evaluated correctly in sets
    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        return isinstance(other, Operation) and self.uuid == other.uuid

class PGraph:
    """
    General P-graph structure consisting of material (M-type) and
    operation (O-type) nodes.
    """
    def __init__(self, m: set[Material], o: set[Operation]):
        self.m = set(m)
        self.o = set(o)

    @property
    def arcs(self) -> set[tuple]:
        arcs = set()
        for operation in self.o:
            for material in operation.m_in:
                arcs.add((material, operation))
            for material in operation.m_out:
                arcs.add((operation, material))
        return arcs

    @property
    def graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_nodes_from(self.m, nodetype="m")
        graph.add_nodes_from(self.o, nodetype="o")
        graph.add_edges_from(self.arcs)
        return graph

    @property
    def labels(self) -> dict:
        return {node: node.name for node in self.graph.nodes}

    @property
    def isnull(self) -> bool:
        return isempty(self.m) and isempty(self.o)

    def write_png_pydot(self, pathname):
        pydot_graph = nx.nx_pydot.to_pydot(self.graph)
        for node in pydot_graph.get_node_list():
            node.set_fontname("arial")
            if node.get_attributes().get("nodetype") == "o":
                node.set_shape("box")
                node.set_style("filled")
                node.set_fillcolor("lightblue")
            else:
                node.set_shape("plain")
        pydot_graph.set_dpi(300)
        pydot_graph.write_png(pathname)

def mat_out(o: set[Operation]) -> set[Material]:
    mat_out_set = set()
    for operation in o:
        mat_out_set.update(operation.m_out)
    return mat_out_set

def mat_in(o: set[Operation]) -> set[Material]:
    mat_in_set = set()
    for operation in o:
        mat_in_set.update(operation.m_in)
    return mat_in_set

def mat(o: set[Operation]) -> set[Material]:
    return mat_in(o) | mat_out(o)

def Del(X: Material, O: set[Operation]) -> set[Operation]:
    return {op for op in O if X in op.m_out}

class StructuralModel(PGraph):
    def __init__(self, P: set[Material], R: set[Material], O: set[Operation]):
        self.P = P.copy()
        self.O = O.copy()
        self.R = R.copy()

        # CORRECT LOGIC: Automatically augment raw materials upon initialization
        self.augment_raw_materials()

        self.m = self.P | self.R | mat(self.O)
        self.o = self.O
        self.O_max = set() # Will store pruned operations after MSG

    def augment_raw_materials(self):
        """
        Algorithm 1: Finds materials that are inputs but are never produced, 
        and adds them to the raw material set R.
        """
        mat_O = mat(self.O)
        mat_out_O = mat_out(self.O)
        R_cand = mat_O - mat_out_O
        self.R = self.R | R_cand

    def generate_maximal_structure(self) -> PGraph:
        P = self.P.copy() 
        R = self.R.copy()

        # Remove operations producing raw materials
        O = {op for op in self.O if isempty(op.m_out & R)}
        M = mat(O)

        if not P <= M:
            return PGraph(set(), set()) # No maximal structure exists

        O_m_out = mat_out(O)

        # Materials only consumed, but not raw materials
        T = {m for m in M if m not in R and m not in O_m_out}

        while not isempty(T):
            X = T.pop()
            O_X = {op for op in O if X in op.m_in}
            O = O - O_X
            M = mat(O)
            if not P <= M:
                return PGraph(set(), set()) 

            T_ = {m for m in mat_in(O) if m in mat_out(O_X) and m not in mat_out(O)}
            T = (T & M) | T_

        # Composition step
        W = P.copy() 
        m_inc = set() 
        o_inc = set() 

        while not isempty(W):
            X = W.pop()
            m_inc.add(X)
            O_X = {op for op in O if X in op.m_out}
            o_inc.update(O_X)
            W = (W | mat_in(O_X)) - (R | m_inc)

        self.O_max = o_inc # CORRECT LOGIC: Save pruned operations for SSG
        return PGraph(mat(o_inc), o_inc)

    def __ssg(self, p: set, m: set, dm_m: set, ss_list_dm: list):
        if isempty(p):
            ss_list_dm.append(dm_m)
            return

        x = next(iter(p))

        # CORRECT LOGIC: Use self.O_max (Maximal Structure Operations)
        Delx = Del(x, self.O_max) 
        C = powerset(Delx) 

        for c in C: 
            c = set(c) 
            consistent = True
            for y in m:
                dely = set()
                for element in dm_m:
                    if element[0] == y: 
                        dely.update(set(element[1]))

                dely_comp = Del(y, self.O_max) - dely 
                if isempty(c & dely_comp) and isempty((Delx - c) & dely): 
                    pass
                else:
                    consistent = False
                    break

            if consistent:
                new_p = (p | mat_in(c)) - (self.R | m | {x})
                new_m = m | {x}
                new_dm_m = dm_m | {(x, frozenset(c))}
                self.__ssg(new_p, new_m, new_dm_m, ss_list_dm)

    def generate_solution_structures(self, pathways_only=True) -> list[PGraph]:
        """
        Generates solutions. If pathways_only=True, it filters out combinations 
        of processes and returns ONLY irreducible, base chemical process flowsheets.
        """
        max_struct = self.generate_maximal_structure()
        if max_struct.isnull:
            print("No maximal structure exists. Solutions impossible.")
            return []

        ss_list_dm = []
        ss_list = []

        if isempty(self.P):
            print("No solution structure exists (No Product specified)")
            return []

        # Run recursive SSG
        self.__ssg(self.P, set(), set(), ss_list_dm)

        # Compile structures
        for e in ss_list_dm:
            o_sets = {el[1] for el in e}
            o = set()
            for subset in o_sets: 
                o.update(subset)
            ss_list.append(PGraph(m=mat(o), o=o))

        # CORRECT LOGIC: Filter for Irreducible Pathways (No combined parallel paths)
        if pathways_only and ss_list:
            irreducible_pathways = []

            # A pathway is irreducible if its operations are not a superset of another valid pathway
            for s1 in ss_list:
                is_irreducible = True
                for s2 in ss_list:
                    if s1 != s2 and s2.o.issubset(s1.o):
                        is_irreducible = False
                        break
                if is_irreducible:
                    irreducible_pathways.append(s1)

            return irreducible_pathways

        return ss_list
