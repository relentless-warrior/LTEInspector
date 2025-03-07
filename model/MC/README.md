1. Domain-Specific Language (DSL) to model the protocol:
irV4.xml: Define the protocol behaviors (e.g., states, transitions and variables) in XML 

2. Run ir2smv.py to convert the DSL to the SMV model (e.g., LTE.SMV): $ python2.7 ir2smv.py
   After executing this command, you will also get dot files representing the finite state machines of the protocol participants (e.g., UE and MME)

3. Run nuSmv:
./nuSmv -int LTE.smv
read_model
flatten_hierarchy
encode_variables
build_boolean_model
check_ltlspec_klive   
