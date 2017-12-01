#!/usr/bin/env python
"""
simple script to visualize the trace output of smv / NuSMV
via Graphviz's dot-format. first, the trace is parsed and
then coded as dot-graph with states as nodes and input 
(transitions) as arcs between them. even if the counterexample's
loop start- and end-state are the same, they are represented by
two different nodes as there can be differences in the completeness
of the state variables' representation.

this is only a simple hack to get quick and dirty trace graphs ;-)
"""

import os,sys,getopt
from collections import OrderedDict
digraph = ""

try:
   import pydot
except:
   print ("this module depends on pydot\nplease visit http://dkbza.org/ to obtain these bindings")
   sys.exit(2)

# CHANGE HERE:
VIEW_CMD="gv -antialias" #used as: VIEW_CMD [file]
DOT_CMD="dot -Tps -o" #used as:    DOT_CMD [outfile] [infile]
TEMPDIR="/tmp"        #store dot-file and rendering if viewmode without output-file


# for internal purposes, change only, if you know, what you do
DEBUG=False
PROFILE=False
PSYCO=True
if PSYCO:
   try:
      import psyco
   except (ImportError, ):
      pass
   else:
      psyco.full()
      if DEBUG: print ("psyco enabled")



def trace2dotlist(traces):
    """this function takes the trace output of (nu)smv as a string;
    then, after cleaning the string of warnings and compiler messages,
    decomposes the output into separate single traces which are translated
    to dot-graphs by _singletrace2dot. as a traceoutput can combine several
    traces, this method returns a list of the dot-graphs"""

    # beautify ;-)

    lines = [line for line in traces if not (line.startswith("***") or
      line.startswith("WARNING") or line == "\n")]

    map(lambda x: x.lstrip("  "), lines)

    # cut list at each "-- specification"
    index=0
    trace_list=[]
    # trace_list = traces for multiple properties.
    # each trace consists of sequence of states.
    # each state consists of a list of variables and their values

    for line in lines:
        if line.startswith("-- specification"):
            # TODO: need to commemnt out the following line
            # formulae = item.rstrip("is false\n").lstrip("-- specification")
            last = index
            index = lines.index(line)
            trace_list.append(lines[last: index])
    trace_list.append(lines[index: len(lines)])

    #sort out postive results. And filter out the empty trace.
    trace_list = [trace for trace in trace_list if len(trace)>1 and not str(trace[0]).endswith("true")]

    # Draw graph for each trace
    graph=[]
    for trace in trace_list:
        graph.append(_singletrace2dot(trace,True))
   
    return graph
   

def _singletrace2dot(trace,is_beautified=False):
    """translate a single trace into a corresponding dot-graph;
    wheras the parsing assumes a correct trace given as
    trace ::=  state ( input state )*
    """

    # if not is_beautified:
    #     lines = [line for line in trace if not (line.startswith("***") or
    #         line.startswith("WARNING") or line == "\n"
    #              or line.startswith("-- specification") or line.startswith("-- as demonstrated")
    #              or line.startswith("Trace Description: ") or line.startswith("Trace Type: "))]
    #     map(lambda x: x.lstrip("  "), lines)
    # else:
    #     lines = trace

    # strip the headers of each trace.
    global digraph
    lines = []
    for line in trace:
        if( not (line.startswith("***") or
            line.startswith("WARNING") or line == "\n"
                 or line.startswith("-- specification") or line.startswith("-- as demonstrated")
                 or line.startswith("Trace Description: ") or line.startswith("Trace Type: "))):
            lines.append(line.lstrip("  "))

    #print (lines)
    #slice list at "->"
    index=0
    states=[]
    for item in lines:
        if item.startswith("->"):
            last=index
            index=lines.index(item)
            states.append(lines[last:index]) # the first state is empty
    states.append(lines[index:len(lines)])
    #print (ind)

    lines=False #free space!
   
    graph = pydot.Graph()

    loop=False #flag to finally add an additional dotted edge for loop

    assert states[1][0].startswith("-> State:") #starting with state!

    digraph = 'Digraph G{\n'
    digraph += 'rankdir=LR\n'
    stateVariablesDict = OrderedDict()
    counter = 0
    for item in states[1:]: #first item is header
        name= item[0].lstrip("-> ").rstrip(" <-\n")
        if (name.startswith("State")):
            state=name.lstrip("State: ")
            node=pydot.Node(state)
            props=name+'\\n' #to reach pydotfile: need double '\'
            digraph =  digraph + 'S' + str(counter) + '[shape=box,label=\"' + name + '\\n'
            counter = counter + 1
            #print (name)
            for i in (item[1:]):
                #props+=i.rstrip('\n')
                #props+="\\n"
                isNewValue = False
                s = str(i).rstrip('\n')
                variable = s[:s.rfind('=')].strip()
                value = s[s.rfind('=')+1:].strip()

                if(variable not in stateVariablesDict):
                    isNewValue = False
                else:
                    (val, newValInd) = stateVariablesDict[variable]
                    if(str(val) != str(value)):
                        isNewValue = True
                stateVariablesDict[variable] = (value, isNewValue)

            #stateVariablesList = [[k, v] for k, v in stateVariablesDict.items()]

            for var, (val, newValInd) in stateVariablesDict.items():
                if(newValInd == True):
                    props += '*' + sr(var) + ' = ' + str(val) + '\\n'
                    digraph = digraph + '*' + str(var) + ' = ' + str(val) + '\\n'
                else:
                    props += str(var) + ' = ' + str(val) + '\\n'
                    digraph = digraph + str(var) + ' = ' + str(val) + '\\n'

            node.set_label('"'+props+'"')

            digraph = digraph + '\"]\n'

            graph.add_node(node)

            for var, (val, newValInd) in stateVariablesDict.items():
                stateVariablesDict[var] = (val, False)


        elif name.startswith("Input"):
            assert state #already visited state
            trans=name.lstrip("Input: ")
            edge=pydot.Edge(state,trans)

            hasLoop = [it for it in item[1:] if it.startswith("-- Loop starts here")]
            #TODO: check trace-syntax, if this can happen only in the last line of a transition
            #      then list-compreh. can be avoided
            if hasLoop:
                loop=state #remember state at which loop starts
                item.remove(hasLoop[0])

            props=""
            for i in (item[1:]):
                props+=i.rstrip('\n')
                props+="\\n"
                edge.set_label(props)
                graph.add_edge(edge)

        else:
            assert False #only states and transitions!

    if loop:
        edge=pydot.Edge(state,loop)
        edge.set_style("dotted,bold")
        edge.set_label(" LOOP")
        graph.add_edge(edge)

    for i in range(1, counter):
        digraph = digraph + 'S' + str(i-1) + ' -> ' + 'S' + str(i) + '\n'
    digraph = digraph + '\n}\n'

    return graph



def usage():
    print ("usage:")
    print (str(os.path.basename(sys.argv[0]))+" [-h|--help] [-o|--output=<filename>] filename")
    print ()
    print (" -o     : output to file (else to std.output)")
    print (" --view : generate preview &  open viewer")


def main():
    global digraph
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvo:", ["view","help","output="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    outputfilename = None
    verbose = False
    view=False
    tempdir=None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-o", "--output"):
            outputfilename = a
        if o == "--view":
            view=True

    if args.__len__():
        filename=args[0]
        trace = open(filename,'r').readlines()
        #trace.close()
    else:
        trace=sys.stdin.readlines()

    graph= trace2dotlist(trace)

    if outputfilename:
        outputfile=open(outputfilename,'w')
    elif view:
        import tempfile
        tempdir=tempfile.mkdtemp(dir=TEMPDIR)
        outputfilename=os.path.join(tempdir,"trace.dot")
        outputfile=open(outputfilename,'w')
    else:
        outputfile=sys.stdout

    for g in graph:
        outputfile.write(g.to_string())
    outputfile.close()

    # Draw Digraph:
    print (digraph)
    outputfilename = outputfilename + '_digraph.dot'
    outputfile = open(outputfilename, 'w')
    outputfile.write(digraph)
    outputfile.close()

    if view:
        if not tempdir: #for view & output
            import tempfile
            tempdir=tempfile.mkdtemp(dir=TEMPDIR)
        visualgraphfile=os.path.join(tempdir,"trace.ps")
        os.system("%s %s %s"%(DOT_CMD,visualgraphfile,outputfilename))
        os.system("%s %s"%(VIEW_CMD,visualgraphfile))



if __name__=="__main__":
    if DEBUG:
        # for post-mortem debugging
        import pydb,sys
        sys.excepthook = pydb.exception_hook
    elif PROFILE:
        if PSYCO:
            raise (Exception, "cannot profile whilst using psyco!!!")
        import hotshot
        prof = hotshot.Profile("_hotshot",lineevents=1)
        prof.runcall(main)
        prof.close()
    else:
        main()
