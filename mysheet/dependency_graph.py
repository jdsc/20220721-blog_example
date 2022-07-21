from os import stat
from typing import Deque, Generator, Iterable, Sequence, Set
from collections import deque

import jinja2
import networkx as nx
from networkx.exception import NetworkXError
from tqdm import tqdm

from .exceptions import CyclicDependency
from .task import Task


def num_parents(g: nx.DiGraph, n: Task) -> int:
    ps = g.predecessors(n)
    return len(list(ps))


def num_children(g: nx.DiGraph, n: Task) -> int:
    cs = g.successors(n)
    return len(list(cs))


class DependencyGraph:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_dependency(self, parent: Task, child: Task) -> None:
        self.graph.add_edge(parent, child)

    def remove_dependency(self, parent: Task, child: Task) -> None:
        self.graph.remove_edge(parent, child)
        if num_parents(self.graph, parent) == 0 and \
           num_children(self.graph, parent) == 0:
            self.graph.remove_node(parent)
        if num_parents(self.graph, child) == 0 and \
           num_children(self.graph, child) == 0:
            self.graph.remove_node(child)

    def get_parents(self, node: Task) -> Iterable[Task]:
        try:
            return self.graph.predecessors(node)
        except NetworkXError:
            # nodeが、計算グラフに登録されていない場合、NetworkXErrorが起こる
            return []

    def get_children(self, node: Task) -> Iterable[Task]:
        try:
            return self.graph.successors(node)
        except NetworkXError:
            # nodeが、計算グラフに登録されていない場合、NetworkXErrorが起こる
            return []

    def get_calculation_tasks(self) -> Generator[Task, None, None]:
        if not nx.is_directed_acyclic_graph(self.graph):
            raise CyclicDependency()

        clone = nx.DiGraph(self.graph)
        roots: Deque[Task] = deque()
        for node in clone.nodes:
            if num_parents(clone, node) == 0:
                roots.append(node)

        while len(roots) > 0:
            node = roots.popleft()
            for child in clone.successors(node):
                if num_parents(clone, child) == 1:
                    roots.append(child)
            clone.remove_node(node)
            yield node

    def calculate(self) -> None:
        for task in tqdm(self.get_calculation_tasks(), total=len(self.graph)):
            task.run()

    def clear(self) -> None:
        self.graph.clear()

    def update(self, node: Task) -> Sequence[Task]:
        visited: Set[Task] = set()
        stack: Deque[Task] = deque()
        stack.append(node)
        while len(stack) > 0:
            current = stack.pop()
            visited.add(current)
            current.reset()
            children = self.get_children(current)
            for c in children:
                if c in visited:
                    continue
                stack.append(c)
        self.calculate()
        return list(visited)

    def to_dot(self, path: str) -> None:
        template = jinja2.Template("""
digraph {
  graph [
         charset = "UTF-8",
         labelloc = "t",
         labeljust = "c",
         bgcolor = "#343434",
         fontcolor = white,
         fontsize = 18,
         style = "filled",
         rankdir = TB,
         margin = 0.2,
         splines = spline,
         ranksep = 1.0,
         nodesep = 0.9
         ];
  node [
        colorscheme = "rdylgn11",
        style = "solid,filled",
        fontsize = 16,
        fontcolor = 6,
        fontname = "Migu 1M",
        color = 7,
        fillcolor = 11,
        height = 0.6,
        width = 1.2
        ];

  edge [
        style = solid,
        fontsize = 14,
        fontcolor = white,
        fontname = "Migu 1M",
        color = white,
        labelfloat = true,
        labeldistance = 2.5,
        labelangle = 70
        ];

{% for e in edges %}
"{{e[0].name}}" -> "{{e[1].name}}";
{% endfor %}

{% for n in nodes %}
"{{n.name}}" [ shape = ellipse ];
{% endfor %}
}
""")

        edges = self.graph.edges
        nodes = self.graph.nodes

        lines = template.render(dict(
            edges=edges,
            nodes=nodes
        ))

        with open(path, "w") as f:
            f.write(lines)


_SINGLETON = DependencyGraph()


def get() -> DependencyGraph:
    return _SINGLETON


def clear() -> None:
    _SINGLETON.clear()
