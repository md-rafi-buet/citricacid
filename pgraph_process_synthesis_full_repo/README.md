# P-Graph Process Synthesis

A Python framework and set of case studies for P-Graph-based process synthesis, including:
- a reusable core module (`pgraph/core.py`)
- a PLA example
- industrial citric acid biorefinery examples
- GraphViz export of maximal structures and solution structures

## Repository layout

```text
pgraph-process-synthesis/
├── pgraph/
│   ├── __init__.py
│   └── core.py
├── examples/
│   ├── pla_case_study.py
│   ├── citric_acid_option_a.py
│   ├── citric_acid_option_b.py
│   └── citric_acid_industrial_option_a.py
├── graphs/
├── graphs_citric_acid_Option_A/
├── graphs_citric_acid_Option_B/
├── README.md
├── requirements.txt
├── pyproject.toml
├── LICENSE
└── .gitignore
```

## Requirements

- Python 3.10+
- `networkx`
- `pydot`
- Graphviz installed on the system for PNG export

## Installation

```bash
pip install -r requirements.txt
```

## Running the examples

```bash
python examples/pla_case_study.py
python examples/citric_acid_option_a.py
python examples/citric_acid_option_b.py
python examples/citric_acid_industrial_option_a.py
```

## Notes

- `Option A` models wastes explicitly as material nodes.
- `Option B` stores waste metadata in the operation properties to keep `|β| = 1`.
- The industrial citric acid example is the most detailed case study in this repository.
