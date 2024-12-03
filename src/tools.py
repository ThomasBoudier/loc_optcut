from z3 import *
import os
import glob
import igraph
import matplotlib.pyplot as plt
import random
import copy
import time
from multiprocessing import Pool
import string

def read_settings():
    with open('settings.txt', 'r') as f:
        L = f.readline()
        L = L.split(";")
        return L
    
GRAPH_PATH,LAYOUT_PATH,SAVING_PATH_TXT,SAVING_PATH_IMG,EXTRA_NAME,CORE_USED,PROBLEM, N,NG = read_settings()
# due to some BAD programming these are strings containing strings. Hence the following thing:
GRAPH_PATH = GRAPH_PATH[:len(GRAPH_PATH)-1][1:]
print(GRAPH_PATH)
LAYOUT_PATH = LAYOUT_PATH[:len(LAYOUT_PATH)-1][1:]
SAVING_PATH_TXT[:len(SAVING_PATH_TXT)-1][1:]
SAVING_PATH_IMG = SAVING_PATH_IMG[:len(SAVING_PATH_IMG)-1][1:]
EXTRA_NAME = EXTRA_NAME[:len(EXTRA_NAME)-1][1:]
PROBLEM[:len(PROBLEM)-1][1:]
N = int(N[:len(N)-1][1:])
CORE_USED = CORE_USED[:len(CORE_USED)-1][1:]
NG = int(NG[:len(NG)-1][1:])
function_file = 'data/automation/function'

Ng, Ngadget = NG, NG
PROCESSES = 2**8        #number of different slices
target = int(N)-Ngadget-8         #length of a slice id
EXEC_BLOCK = 2**14      #slices are executed EXEC_BLOCK at a time at most (2^14 = ~16k)

def return_layout():
    """return the layout of the graph. By hand, sadly. Layouts are of the form [(xi,yi)]""" 
    #a Layout looks like this:
    #(3,7),(4,7),(3,6),(4,6),(3,5),(4,5),(3,9),(4,9),(2,8),(3,8),(4,8),(5,8),(2,7),(5,7),(2,6),(5,6),(2,5),(5,5),(2,4),(3,4),(4,4),(5,4),(3,3),(4,3),(3,10),(4,10),(2,9),(5,9),(1,7),(6,7),(1,5),(6,5),(2,3),(5,3),(3,2),(4,2),(3,11),(4,11),(2,10),(5,10),(1,9),(6,9),(1,8),(6,8),(1,6),(6,6),(1,4),(6,4),(1,3),(6,3),(2,2),(5,2),(3,1),(4,1)
    with open(LAYOUT_PATH, 'r') as f:
        L = f.readline()
    R = []
    x = ''
    for c in L:
        if c == '(':
            begin_node = True

        if c == ')':
            begin_node = False
            #at this point x looks like '(3,14'
            #remains to remove parenthesis and split at ','.
            x = x[1:]
            x = x.split(',')
            R.append((int(x[0]), int(x[1])))
            x = ''
        if begin_node:
            #then we copy c at x
            x+=c    
    return R

def return_adj_matrix(path = GRAPH_PATH):
    """return the adjacency matrix. Takes the hog file stocked at GRAPH_PATH"""
    with open(path, 'r') as f:
        X= []
        for line in f.readlines():
            L = []
            for c in line:
                if c == '1':
                    L.append(1)
                elif c == '0':
                    L.append(0)
            if L != []:
                X.append(L)
    return X

def auto_function(problem = '2-2-3'):
    """creates the problem on the matrix. problem = PROBLEM. """
    mat = return_adj_matrix()
    X = [Int("x[%s]"%i) for i in range(N)] #theres more variables than necessary but who cares
    #bools = [X[i]>=0 for i in range(Nt)] + [X[i]<= 1 for i in range(Nt)]               #not necessary here
    if problem == '2-2-3':
        cst1 = [X[i]*sum([X[j] for j in range(Ngadget, N) if mat[i][j]==1])<=1 for i in range(Ngadget,N)]
        cst2 =  [(1-X[i])*sum([(1-X[j]) for j in range(Ngadget, N) if mat[i][j]==1])<=1 for i in range(Ngadget,N)]
    elif problem == '3-2-5':
        cst1 = [X[i]*sum([X[j] for j in range(NG, N) if mat[i][j]==1])<=2 for i in range(NG,N)]
        cst2 =  [(1-X[i])*sum([(1-X[j]) for j in range(NG,N) if mat[i][j]==1])<=2 for i in range(NG,N)]

    with open(function_file , 'w') as f:
        xstr = '('
        for i in cst1:
            xstr += str(i)+') and ('
        for i in cst2[1:]:
            xstr += str(i)+ ') and ('
        xstr += str(cst2[len(cst2)-1])+')'
        f.write(xstr)

def auto_verification(k):
    """takes k in input (string of 0's and 1's) and verify using the automatically generated function that it's a valid input."""
    x = [0]*Ngadget + [int(ki) for ki in k]  
    return (x[24]*(0 + x[36] + x[38]) <= 1) and (x[25]*(0 + x[37] + x[39]) <= 1) and (x[26]*(0 + x[38] + x[40]) <= 1) and (x[27]*(0 + x[39] + x[41]) <= 1) and (x[28]*(0 + x[42] + x[44]) <= 1) and (x[29]*(0 + x[43] + x[45]) <= 1) and (x[30]*(0 + x[44] + x[46]) <= 1) and (x[31]*(0 + x[45] + x[47]) <= 1) and (x[32]*(0 + x[48] + x[50]) <= 1) and (x[33]*(0 + x[49] + x[51]) <= 1) and (x[34]*(0 + x[50] + x[52]) <= 1) and (x[35]*(0 + x[51] + x[53]) <= 1) and (x[36]*(0 + x[24] + x[37]) <= 1) and (x[37]*(0 + x[25] + x[36]) <= 1) and (x[38]*(0 + x[24] + x[26]) <= 1) and (x[39]*(0 + x[25] + x[27]) <= 1) and (x[40]*(0 + x[26] + x[42]) <= 1) and (x[41]*(0 + x[27] + x[43]) <= 1) and (x[42]*(0 + x[28] + x[40]) <= 1) and (x[43]*(0 + x[29] + x[41]) <= 1) and (x[44]*(0 + x[28] + x[30]) <= 1) and (x[45]*(0 + x[29] + x[31]) <= 1) and (x[46]*(0 + x[30] + x[48]) <= 1) and (x[47]*(0 + x[31] + x[49]) <= 1) and (x[48]*(0 + x[32] + x[46]) <= 1) and (x[49]*(0 + x[33] + x[47]) <= 1) and (x[50]*(0 + x[32] + x[34]) <= 1) and (x[51]*(0 + x[33] + x[35]) <= 1) and (x[52]*(0 + x[34] + x[53]) <= 1) and (x[53]*(0 + x[35] + x[52]) <= 1) and ((1 - x[25])*(0 + 1 - x[37] + 1 - x[39]) <= 1) and ((1 - x[26])*(0 + 1 - x[38] + 1 - x[40]) <= 1) and ((1 - x[27])*(0 + 1 - x[39] + 1 - x[41]) <= 1) and ((1 - x[28])*(0 + 1 - x[42] + 1 - x[44]) <= 1) and ((1 - x[29])*(0 + 1 - x[43] + 1 - x[45]) <= 1) and ((1 - x[30])*(0 + 1 - x[44] + 1 - x[46]) <= 1) and ((1 - x[31])*(0 + 1 - x[45] + 1 - x[47]) <= 1) and ((1 - x[32])*(0 + 1 - x[48] + 1 - x[50]) <= 1) and ((1 - x[33])*(0 + 1 - x[49] + 1 - x[51]) <= 1) and ((1 - x[34])*(0 + 1 - x[50] + 1 - x[52]) <= 1) and ((1 - x[35])*(0 + 1 - x[51] + 1 - x[53]) <= 1) and ((1 - x[36])*(0 + 1 - x[24] + 1 - x[37]) <= 1) and ((1 - x[37])*(0 + 1 - x[25] + 1 - x[36]) <= 1) and ((1 - x[38])*(0 + 1 - x[24] + 1 - x[26]) <= 1) and ((1 - x[39])*(0 + 1 - x[25] + 1 - x[27]) <= 1) and ((1 - x[40])*(0 + 1 - x[26] + 1 - x[42]) <= 1) and ((1 - x[41])*(0 + 1 - x[27] + 1 - x[43]) <= 1) and ((1 - x[42])*(0 + 1 - x[28] + 1 - x[40]) <= 1) and ((1 - x[43])*(0 + 1 - x[29] + 1 - x[41]) <= 1) and ((1 - x[44])*(0 + 1 - x[28] + 1 - x[30]) <= 1) and ((1 - x[45])*(0 + 1 - x[29] + 1 - x[31]) <= 1) and ((1 - x[46])*(0 + 1 - x[30] + 1 - x[48]) <= 1) and ((1 - x[47])*(0 + 1 - x[31] + 1 - x[49]) <= 1) and ((1 - x[48])*(0 + 1 - x[32] + 1 - x[46]) <= 1) and ((1 - x[49])*(0 + 1 - x[33] + 1 - x[47]) <= 1) and ((1 - x[50])*(0 + 1 - x[32] + 1 - x[34]) <= 1) and ((1 - x[51])*(0 + 1 - x[33] + 1 - x[35]) <= 1) and ((1 - x[52])*(0 + 1 - x[34] + 1 - x[53]) <= 1) and ((1 - x[53])*(0 + 1 - x[35] + 1 - x[52]) <= 1) and ((1 - x[53])*(0 + 1 - x[35] + 1 - x[52]) <= 1) and ((1-x[24])*(1- x[36] + 1-x[38]) <= 1)

def cleanup():
    """ clean the slices. """
    PROCESSES = 2**8        #number of different slices
    target = 0      #length of a slice
    EXEC_BLOCK = 2**14      #slices are executed EXEC_BLOCK at a time at most (2^14 = ~16k)
    create_slices(target)
    with open("data/save_to_look_at.txt", 'w') as f:
        f.write('')

def create_slices(target):
    for processid in range(PROCESSES):
        fprocess = open('data/slices/slice_'+'{0:08b}'.format(processid), 'w')
        fprocess.write('0'*target)
        fprocess.close()

def basic_read():
    ### open all files; for each print the value of the first item in 10th base
    ## hence for 2nd file '00000001', will print the value of 00000001000000000....0
    for processid in range(PROCESSES):
        with open('data/slices/slice_'+'{0:08b}'.format(processid), 'r') as f:
            input = f.readline()
            number = '{0:08b}'.format(processid)+input
            print(int(number,2))

def read_input(FILE_NUMBER):
    #read and print the first input of given file (as a int)
    file_id = '{0:08b}'.format(FILE_NUMBER)
    with open('data/slices/slice_'+file_id, 'r') as f:
        input_file = f.readline()
    return input_file

def pop(self, file):
    """pop the first line from given file (aka removes it from the input file)"""
    with open(file, 'r+') as f: 
        # open file in read / write mode
        firstLine = f.readline() # read the first line and throw it out
        data = f.read() # read the rest
        f.seek(0) # set the cursor to the top of the file
        f.write(data) # write the data back
        f.truncate() # set the file size to the current size
        return firstLine

def fifo(input):
    """pop the first line of the file."""
    return pop(input, input)

def draw_save_to_loook_at(extra=''):
    ''' pop lines from save_to_look_at and print them according to the current problem layout (see automation.py)'''
    mat = return_adj_matrix()
    lay0 = return_layout()
    G = igraph.Graph.Adjacency(mat, mode = 'undirected')
    file = open('data/save_to_look_at.txt', "r")
    while len(file.readlines())>0:
        line = fifo('data/save_to_look_at.txt')
        line = line[:len(line)-1]
        file = open('data/save_to_look_at.txt', 'r')
        col = ['red'*(i=='1')+'green'*(i=='0')+'gray'*(i=='2') for i in line]
        filename = 'data/img/'+extra+line+'.png'
        #print(filename)
        print(G, [i for i in range(N)], filename,  col, lay0)
        igraph.plot(G, vertex_label=[i for i in range(N)], target =filename, vertex_color = col, layout = lay0)
        file.close()

def plot_randomization():
    """open savefile and plot the randomization results in %age"""
    savefile = 'data/quick-randomization.txt'
    def recollect_random():
        with open(savefile, 'r') as f:
            L = f.readlines()
        #print(L)
        output = []
        for line in L:
            output_line=[]
            #print(line)
            output_line = line.split(',')
            #print(output_line)
            output.append(output_line)
        return output
    data = recollect_random() #aka opens savefile and (...)
    print(data, len(data))
    plt.plot([float(k[0]) for k in data if float(k[0])<0.05], [float(k[1]) for k in data if float(k[0])<0.05])
    plt.xlabel("percent of nodes with an initial input")
    plt.ylabel("success probablity")
    plt.savefig('fig.png')

mat = return_adj_matrix()

def hard_solver(k,mat = mat, n=N, nG=Ngadget, mode = 'gadget', problem = '2-2-3'):
    """call z3 and try to solve the problem. Note: ignore the whole "gadget" concept and rather run everything as random mode aka all nodes have an input 0,1 or 2 and we just ignore the existence of those that have 2 as input.

    MODES
    normal - Ng first nodes are a gadgets. 
    minimal - Ng are gadget and some nodes after may have 2 as input - aka no input. 
    random - no gadget, some nodes have input, some other not. must have len(k) = nG = n in this mode 
    random-input - same as random but test the validity of the input in itself
    quick-random - Returns None or a solution. input is 01000... where 0 means to ignore this node. and 1 means the node is present. the input is NOT an "input" but rather a "proof of existence" in the graph. 
    gadget_research - all ng first nodes MUST have the same color. 
    solution - get any solution. no input.

    PROBLEM
    2-2-3, 3-2-5 implemented
    """    

    X = [Int("x[%s]"%i) for i in range(n)]
    bools = [X[i]>=0 for i in range(n)] + [X[i]<= 1 for i in range(n)]
    cst1, cst2, instance = [],[], []

    #NOTE: e.g. for 3-2-5; vx=1 => Y neighbor is of x has sum_{y in Y} vy <= 2
    #all formulas are supposed to reflect this kind of expressions.
    #sometime the input comes as a list of ints being 012210010...
    #0 and 1 are classic colors; 2 is a special color "to ignore" s.t.: no input here for now
    
    if problem == '2-2-3':
        cst1 = [X[i]*sum([X[j] for j in range(n) if mat[i][j]==1])<=1 for i in range(n)]
        cst2 =  [(1-X[i])*sum([(1-X[j]) for j in range(n) if mat[i][j]==1])<=1 for i in range(n)]
    elif problem == '3-2-5':
        cst1 = [X[i]*sum([X[j] for j in range(n) if mat[i][j]==1])<=2 for i in range(n)]
        cst2 =  [(1-X[i])*sum([(1-X[j]) for j in range(n) if mat[i][j]==1])<=2 for i in range(n)]
    if problem == '3-2-5' and (mode =='random-input'):
        cst1 = [X[i]*sum([X[j] for j in range(n) if (mat[i][j]==1 and k[j]!=2)] )<=2 for i in range(n) if X[i]!=2]
        cst2 =  [(1-X[i])*sum([(1-X[j]) for j in range(n) if (mat[i][j]==1 and k[j]!=2)])<=2 for i in range(n) if X[i]!=2]
    if problem == '3-2-5' and mode == 'minimal':
        s=len(k)
        cst1 = [X[i]*sum([X[j] for j in range(s) if mat[i][j]==1])<=2 for i in range(s)]
        cst2 = [(1-X[i])*sum([(1-X[j]) for j in range(s) if mat[i][j]==1])<=2 for i in range(s)]
    #in case of quick random - we only care about the nodes in the input aka; input is labelled as 00010111... where 1 means we care about this node.
    if problem == '3-2-5' and (mode =='quick-random'):
        cst1 = [X[i]*sum([X[j] for j in range(n) if (mat[i][j]==1 and k[i]==1 and k[j]==1)] )<=2 for i in range(n)] 
        cst2 =  [(1-X[i])*sum([(1-X[j]) for j in range(n) if (mat[i][j]==1 and k[i]==1 and k[j]==1)])<=2 for i in range(n)]

    if mode == 'gadget':
        instance =[X[i+nG] == k[i] for i in range(len(k))]    
    elif mode == 'minimal' or mode == 'random-input':
        instance = [If(k[i]!=2, X[i]==k[i], X[i]>=0) for i in range(len(k))]
        #instance =[X[i] == k[i] for i in range(length) if k[i]!= 2 ]    
    if mode == 'random': # or mode == 'random-input':
        #here same as minimal but no gadget.
        instance =[X[i] == k[i] for i in range(len(k)) if k[i]!=2]    
    if mode == 'quick-input': #no instance in this case.
        instance = [] 
    if mode == 'gadgets_research':
        instance = [sum([X[i]*(1-X[j]) for i in range(nG) for j in range(nG)])>=1]
    if mode == 'solution':
        instance = []

    s=Solver()
  
    s.add(bools+cst1+cst2+instance)
    if mode == 'solution':
        if s.check()==sat:
            m = s.model()
            return [m.evaluate(X[i]) for i in range(n)]
    if mode == "quick-random" :
        if s.check()==sat:
            m = s.model()
            #we cannot just return [m.evaluate(X[i]) for i in range(n)] as we just want a solution on input.
            return [m.evaluate(X[i]) if k[i]==1 else 2 for i in range(n)]
        else:
            return None
    if s.check()==sat:
        return True
    else:
        return False
    
def minimal_input(file_name, base_time = 1800, tampon_size = 12):
    """open file and try to find minimal reason as to why it has no solution. base-trying time is set at 600 s. """
    #as per previous test it is not reasonable to do it exhaustively so we have to use a randomized solution. Idea:
    #let p~= n/2. Try some random set of p nodes as a sub input. if one is not solvable -> try to do the exhaustive thing from this starting point. 
    # if after a reasonable amount of testing nothing happened yet try set p++.   

    #1. retrieve the input. set p at n/2
    #2. while we have enough time...
        #2a take a random subset of size p
        #2b test if it is unsovable.
        #if it isnt apply algorithm on this new input and print information onscreen about the said input
        #if not do nothing
    #3. when you run out of time; set back time counter to 0 and try p++.
    #1
    with open(file_name, 'r') as f:
        inp = f.readline() # will be a string like 0102011(..)
    L = [int(x) for x in inp]
    n = len(L) #size of input

    #2
    flag = False #aka were still trying to find some good value for p
    p = n//2 #p = number of nodes we will ommit
    

    while flag == False:    
        time_init=time.time()
        while time.time()<time_init+base_time:
            samp = random.sample(range(n),p)
            candidate_input = copy.deepcopy(L)
            for i in samp:
                candidate_input[i] = 2

            #now test if this candidate input is solvable or not.
            truth = hard_solver([2]*(tampon_size)+candidate_input, n = 48, mode='minimal', problem='3-2-5')
            if truth == False: #then we are happy! 
                #thus we can use this as a base for algorithm.
                
                print("candidate for input found with %d values:"%(n-p))
                print(candidate_input)
                #additional stuff TODO that is NOT what is below
                if sum([1 for i in candidate_input if i!=2])<15:
                    tree_search2([2]*tampon_size+candidate_input)
                    return None
                else:
                    p+=1
        #if we reached this point probably that p is to low (or we were unlucky)
        print('%d values were insufficient. Trying with %d'%(n-p, n-p+1))
        p+=-1

def tree_search2(inp):
    best = [len(inp)]
    tree_search2_aux(inp,0,best,0)

def tree_search2_aux(inp, start, best, recursion_depth):
    if recursion_depth < 5:
        print("Recursion depth=%d, start=%d" % (recursion_depth,start))
    solvable = hard_solver(inp, n = 48, mode='minimal', problem='3-2-5')
    if (start - inp[:start].count(2)) >= best[0]:
        return solvable
    if solvable:
        return True
    all_solvable = True
    for i in range(start,len(inp)):
        if inp[i] != 2:
            t = inp[i]
            inp[i] = 2
            all_solvable &= tree_search2_aux(inp,i+1,best,recursion_depth+1)
            inp[i] = t
    if all_solvable:
        value = len(inp) - inp.count(2)
        if value < best[0]:
            best[0] = value
            print("Found leaf with %d fixed values" % (value))
            print(inp)
    return False

def tree_search(inp):
    """inp: list of ints as 0122210... that must contain a value for all nodes.
    2: corresponding node is not useful
    1 or 0: given color.
    
    Do a tree-search to get a minimal input."""

    def create_node(IN, i):
        #create a clone of IN with IN[i]=2
        INP = copy.deepcopy(IN)
        INP[i]=2
        return INP

    def process_node(IN):
        #look if there are some parts of IN where we can try to flip a 0/1 by a 2.
        #idx = max([0]+[i for i in range(len(IN)) if IN[i]==2]) #look for the position of the last 2 - it was useful before but now it will make us lose part of the solutions
        candidates = [i for i in range(len(IN)) if IN[i]!=2] #where 2's aren't
        if len(candidates) == 0:
            return []
        p = [] #p is a pile of new candidates.
        for c in candidates:
            INP = create_node(IN,c)
            if hard_solver(INP, n = 48, mode='minimal', problem='3-2-5')==False: #hence IN is not minimum
                p.append(INP)
        return p #this is pile to be added to p1. If empty -> then somewhere it has to be detected and added to the minimal list

    def process_pile(p1):
        # empty pile 1 into pile 2. then for each node, call process node.
        leaves = []
        p2 = []
    
        for IN in p1:
            p = process_node(IN)
            if len(p) == 0:
                leaves.append(IN)
            else:#else we have new candidates to p2.
                for pi in p:
                    if p2.count(pi)==0:
                        p2.append(pi)
        return p2, leaves
    
    def algorithm(inp):
        p1 = [inp]
        leaves = []
        t0 = time.time()
        k =0
        while len(p1)!=0:
            p1, leaves = process_pile(p1)
            k+=1
            print('time since start %d, pile emptied %d'%(time.time()-t0, k))
        return leaves
    
    candidate_leaves = algorithm(inp)
    L = []
    for leaf in candidate_leaves:
        if L.count(leaf) == 0:
            L.append(leaf)
    with open('data/leaves.txt', 'w') as f:
        for leaf in L:
            f.write(leaf)

def settings():
    """interface to modify settings.txt"""
    with open('settings.txt') as f:
            content = f.readline()
            content = content.split(';')

    def print_settings(content):
        for f in range(len(content)):
            print(setting_name(f) +' - ' +content[f])

    def setting_name(i):
        #handy for new_setting function
        if i == 0:
            return 'GRAPH_PATH'
        if i == 1:
            return 'LAYOUT_PATH'
        if i == 2:
            return 'SAVING_PATH_TXT'
        if i == 3:
            return 'SAVING_PATH_IMG'
        if i == 4:
            return 'EXTRA_NAME'
        if i == 5:
            return 'CORE_USED'
        if i == 6:
            return 'PROBLEM'
        if i == 7:
            return 'N'
        if i == 8:
            return 'NG'
        
    def identify_name(user_input):
        #= understand which line is to be modify. 
        if user_input == 'GRAPH_PATH':
            return 0
        if user_input == 'LAYOUT_PATH':
            return 1
        if user_input == 'SAVING_PATH_TXT':
            return 2
        if user_input == 'SAVING_PATH_IMG':
            return 3
        if user_input == 'EXTRA_NAME':
            return 4
        if user_input =='CORE_USED':
            return 5
        if user_input == 'PROBLEM':
            return 6
        if user_input == 'N':
            return 7
        if user_input == 'NG':
            return 8

    def new_setting(i,string,content):
        #a = setting_name(i)
        content[i] ="'"+string+"'"
        return content 
    
    def reset():
        return "'data/adjs/flower_48.txt';'data/layouts/flower_48.txt';'data/save_to_look_at.txt';'data/img';'';'4';'3-2-5';'48';'12"
    
    user_input = ''
    print("Type for instance 'CORE_USED' to modify the number of cores. Current settings are the following:")
    print_settings(content)
    print("other commands: exit - print - save - reset")
    while user_input != 'exit':
        user_input=input('Type a command:')
        
        if user_input == 'GRAPH_PATH' or user_input == 'LAYOUT_PATH' or user_input == 'SAVING_PATH' or user_input == 'EXTRA_NAME' or  user_input =='CORE_USED':
            id = identify_name(user_input)
            user_input = input("Enter new settings: ")
            #content = new_setting(id, user_input,content)
            new_setting(id,user_input,content)
            with open('settings.txt', 'w') as f:
                for line in content:
                    f.write(line+';')
            print(setting_name(id) + ' set to ' + user_input)

        if user_input == 'print':
            print_settings(content)
        
        if user_input == 'save':
            with open('settings.txt', 'w') as f:
                for line in content:
                    if line != content[-1]: #NOTE: this can and WILL create problems in case of settings being identical.
                        f.write(line+';')
                    else: 
                        f.write(line)
        if user_input == 'reset':
            with open('settings.txt', 'w') as f:
                x = reset()
                f.write(x)
            print('current settings:')
            with open('settings.txt') as f:
                content = f.readline()
                content = content.split(';')
            print_settings()

def exhaustive():
    """exhaustive exploration of inputs on the graph. Bad inputs are saved."""

    CHUNKSIZE = 2**14 #arbitrary value - too low and youll slow down too much
                        #too high and you may lose some time in case of multiple sessions
    def executor(file_number):
        """execute CHUNKSIZE operations of the corresponding file"""
        file_id = '{0:08b}'.format(file_number)
        with open('data/slices/slice_'+file_id, 'r') as f:
            starting_value = int(file_id+f.readline(), 2)

        for k in range(CHUNKSIZE):
            input = starting_value + k
            input_b = '{0:030b}'.format(input) #=total input even counting the slide id
            #print(input_b, input, type(input_b), type(input))
            if auto_verification(input_b):
                if hard_solver(input_b, mat, N, NG, mode = 'gadget', problem = PROBLEM)==False:
                    with open('data/save_to_look_at.txt', 'a') as f:
                        f.write(input_b+'\n')
        with open('data/slices/slice_'+file_id, 'w') as f:
            f.write(input_b[8:])

    def parallel_executor():
        i = 0
        step = 100*(2**14/2**22) #=chuksize/total work per slice
        progress = 0    
        t0 = time()
        print('commencing process...')
        while(progress<100):
            p = Pool(4)
            p.map(executor, range(PROCESSES))
            i+=1
            progress += step
            os.system('clear')
        #TODO to have a coherent print status think to change workload when changing the problem
    parallel_executor()

 #next 3 functions are to build the matrix. 

def nodeID(i,j, n):
    return i*n + j

def coordinates(v, n): # useful in case of printing
    return v//n, v%n

def gen_matrix(n): #original code from Dennis
    g = igraph.Graph(n**2)
    lay = [coordinates(v, n) for v in range(n**2)]
    labels = [str(idx) for idx in lay] 
    for i in range(n):
        for j in range(n):
            g.add_edge(nodeID(i,j, n), nodeID((i+1)%n,j,n))
            g.add_edge(nodeID(i,j, n), nodeID(i,(j+1)%n,n))
            if i%2==0 and j%2==0:
                g.add_edge(nodeID(i,j,n), nodeID((i+1)%n,(j+1)%n,n))
            if i%2==0 and j%2==1:
                g.add_edge(nodeID(i,j,n), nodeID((i-1)%n,(j+1)%n,n))
    return g.get_adjacency(), lay, labels 

def quick_task_2(p):
    EXEC = 5000 #change these values for finer testing or bigger graphs
    n = 16
    """sample EXEC times at probability p of nodes. 
        At the difference of quicktask1 - now when node set S in randomly selected we solve PROBLEM on G[S], then see if we can extend a solution to G."""

    savefile = 'data/quick-randomization.txt'
    M, L, I = gen_matrix(n)
    failure = 0
    p = p/1000
    for test in range(EXEC):
        winners = random.sample(range(n**2), int(p*(n**2))) #winners have been selected.
        k = [0]*(n**2)  #probably this can be done faster?
        for w in winners:
            k[w] =1
                
        solution = hard_solver(k, M, n**2, mode = 'quick-random', problem = PROBLEM )
        #solution serves as a base input on G[S]

        t=hard_solver(solution, M, n**2, mode = 'random-input', problem=PROBLEM) 
            
        if t == False:
            failure+=1
            #remove next two lines if you are uninterested in knowing which inputs may fail
            with open(SAVING_PATH_TXT, '+a') as f:
                f.write(solution)
    with open(savefile, 'a') as f:
        f.write(str(p)+ ','+str(failure/EXEC)+','+str(failure)+'\n')
    return failure > 0 #aka at least one faulty input was found

def randomization():
    """forms a nxn toroidal grid; pick some random nodes and some random input for them. Try to solve PROBLEM on them."""
    #to change n go to the definition of quick_task_2
    savefile = 'data/quick-randomization.txt'
    test_range = range(500, 990, 1) #probabilities tested
                                # must be int so one line may need changement in quick_task_i
   
    print("starting tasks.")
    def parallel_task():
        p = Pool(4)
        p.map(quick_task_2, test_range)

    parallel_task()

def randomization2():
    """Use quick_random, but in a dichotomic manner. Starts at 90%. When failure over 5k tests - increase by b, else decrease by b. b starts at 5% value and decrease its value by 10% each time. Use 3 processors, and to the procedure for p-0.1, p and p+0.1"""

    p = 900 #values are decrease by 1000 - hence 900 = 0.9 = 90%
    b = 50 # = 5%
    it = 0
    while b > 10:
        success = quick_task_2(p)
        if success:
            p+=-b
        else:
            p = min(p+b, 998) #hence it never goes past 100%
        b = 95*b/100
        it += 1

        os.system('clear')
        print("Current values: (p, b)= (%d,%d ). Iterations: %d"%(p,b,it))

def save_matrix(M, location):
    """create a file at location and save the content of the matrix; "hog-style"""
    X = ''
    for line in M:
        for e in line:
            X +=str(e)+' '
        X+='\n'
    with open(location, 'w') as f:
        f.write(X)

def gadgets_research(dummy, mode = 'boundary2'):
    """Look for gadgets with special properties
    
    boundary2= nodes that are not of degree 5 have 2 or 1 neighbors. Look for gadgets where low degree nodes have a specific given solution for 3-2-5 (aka all same color - or something else I'll programm later) TODO
    """
    EXEC = 10**3
    savefolder = 'data/matrices/'
    def degree_sequence(L):
        "determine if a degree sequence is realizable or not. See On Realizability of a Set of Integers as Degrees of the Vertices of a Linear Graph, S. L. Hakimi, 1962, theorem 1"
        return sum(L)==2 and sum(L[:len(L)-1])>= L[-1] and sum([1 for i in L if i<5])

    def random_name():
        """return a random name of length 8."""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(8))

    found = 0
    if mode == 'boundary2':
        for n in range(8,16): #number of total nodes in the target gadget
            for _ in range(EXEC):
                correct = False #Is the degree sequence acceptable?
                L=[]
                while correct == False:
                    n1 = random.randint(0,0)
                    #n2 = random.randint(5, n//2) 
                    n2 = 5
                    n2 = n2+ ((n-n2)%2==1)
                    L = [4]*n2+[5]*(n-n2)#[1]*n1+[4]*n2+[5]*(n-n1-n2) #with current params there's only degree 4 or 5 nodes.
                    correct = True# degree_sequence(L)
                G = igraph.Graph.Degree_Sequence(L, method = 'configuration_simple')
            #print(G.get_adjacency())
                test = hard_solver([],G.get_adjacency(),n, n2, mode='gadgets_research', problem = '3-2-5')
                #os.system('clear')
                if test == False:
                    name = random_name() 
                    #print(G.get_adjacency())
                    save_matrix(G.get_adjacency(), savefolder+name)
                    found+=1
                    print("%d gadgets found."%(found))
                





