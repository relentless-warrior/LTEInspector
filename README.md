# LTEInspector
LTEInspector is a model-based and property-driven adversarial testing framework that combines a symbolic model checker (for reasoning trace properties or temporal ordering of different events/actions) and a cryptographic protocol verifier (for reasoning cryptographic constructs, e.g., encryption, integrity protections) in the symbolic attacker model using counter-example guided abstract refinement (CEGAR) principle. 


## Models and properties of LTEInspector 

model/MC: Models and properties for the symbolic model checker NuSmv.

model/CPV: Models and properties for the cryptographic protocol verifier ProVerif.

## Results: 
LTEInspector uncovered 10 new attacks in 4G LTE network specifications. More details about these findings can be found in the research paper published in NDSS'18.

## Paper: 
https://syed-rafiul-hussain.github.io/wp-content/uploads/2018/02/lteinspector.pdf
