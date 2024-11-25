# Varanus Tools

A collection of tools to support Varanus and CSP verification.

## `csp2dot`

This tool converts a CSPStateMachine object to a DOT object or string, to enable simple visulaisation.

### Installation

`csp2dot` relies on `pydot`, which can be installed using
```bash
pip install pydot
```

### Usage

TBD

# Varanus Experiments

To generate LTL formulas along with their corresponding CSP and RML specifications, run the following:
```bash
python generate_random_ltl_csp_rml.py
```
This script will create three subfolders containing the LTL, CSP and RML specifications (all are randomly generated, but consistent, i.e., ltl1.txt, csp1.csp, and rml1.rml corresponds to the same formal specification to monitor, and the same goes for all the other formulas as well). Thanks to the relation amongst all the specifications, we can then run our experiments validating our approach w.r.t. the same formula to verify in terms of monitor synthesis and verification.

To run the experiments on the resulting generated formulas, run the following.

For LTL (it requires Spot library installed):
```bash
python experiments_ltl
```
This will produce the results in the ltl_res.csv file.

For CSP (it requires FDR installed):
```bash
python experiments_csp
```
This will produce the results in the csp_res.csv file.

For RML (it requires RML installed):
```bash
python experiments_rml
```
This will produce the results in the rml_res.csv file.