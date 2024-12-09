from tools import *



def clear():
    os.system('cls' if os.name == 'nt' else 'clear') #note: might need some tuning for different OS

clear()


size_input_in_slice = 20 #size of what is contains in slices. See "What are data/slices" in README

inp = ''
while inp != 'exit':
    print("available commands: \n> help\n> exit\n\n> automation\n> clean-slides\n> draw\n> draw_gadgets\n> erase\n> exhaustive\n> gadgets_research\n> minimal_input\n> randomization\n> randomization2\n> settings\n> test\n")
    inp = input("type a command: ")

    if inp == 'help': 
        print(">automation -- generates automatically the file data/automation/function from the input given.\nIMPORTANT: once automation has been done you must manually copy/paste the content of in src/automation.py of auto_verification")
        print('>clean-slices -- erase the progress of data/slices.')
        print(">draw -- draw all graphs saved as inputs in save_to_look_at.txt. Inputs are relative to what exhaustive_search is doing. ")
        print(">draw_gadgets -- draw all save matrices in data/matrices/. You might want to modify the function to select different folders.\n")
        print(">erase -- remove all content of data/img")
        print(">exhaustive -- exhaustive exploration of all possible inputs on the given graph; bad inputs (non completable ones) are saved.\n")
        print(">exit -- close the programm")
        print(">gadgets_research -- look for small graphs of particular interest. See the content of tools.gadgets_research() to modify research parameters.\n")
        print(">help -- display all commands and their use")
        print('>minimal_input -- given a partial input that has no solution (in data/partial_input.txt) try to find a sub-partial-input of it s.t. it still has no solution.')
        print(">randomization -- one the NxN 5-regular 'grid'; select a random subset of nodes, give them a solution and try to fill the rest of the graph. Results (failures/succes) are saved in quick-randomization.txt.\n") 
        print(">randomization2 -- same idea but using a dichotomic approach.\n")
        print(">settings -- change parameters such as the size of graphs, filenames etc.")
        print(">test -- Try new stuff here.\n")
        tmp = input("Press any key to continue.")

    if inp=='automation':
        auto_function(PROBLEM)
        tmp = input("data automatically generated. Remember to modify the following functions in src/automation.py:\nreturn_adj_matrix (line 21)\nauto_verification (line 96, optional)\nretrun_layout (line 28 - only if you plan to plot & has to be done by hand until the code is changed)\nPress any key to continue.")

    if inp == 'clean-slices':
        cleanup()
        create_slices(size_input_in_slice)
        tmp = input("256 slices of size %d created. Press any key to continue."%(size_input_in_slice))

    if inp == 'draw':
        draw_save_to_loook_at(extra = EXTRA_NAME)
        tmp = input("All figures generated in data/img. Press any key to continue.")

    if inp == 'erase':
        files = glob.glob('/data/img/*')
        for f in files:
            os.remove(f)
        tmp = input("All figures in data/img have been erased. Press any key to continue.")

    if inp== 'minimal_input':
        print("starting minimal input procedure with a base time of 1800s.")
        minimal_input('/data/bad_input.txt', base_time=1800)
    
    if inp == 'settings':
        settings()
    
    if inp == 'exhaustive':
        exhaustive()

    if inp == 'randomization':
        randomization()

    if inp == 'test':
        M = return_adj_matrix()
        print(hard_solver([], M, 9, 5,mode = 'gadgets_research',problem = '3-2-5' ))
        
    if inp == 'erase-random':
        savefile = 'data/quick-randomization.txt'
        with open(savefile, 'w') as f:
            f.write('')
        
    if inp == 'randomization2':
        print("Starting randomization procedure in details")
        randomization2()            

    if inp == 'gadgets_research':
        t0 = time.time()
        p = Pool(4)
        print("Research begin")
        p.map(gadgets_research, range(100))
        t1 = time.time()
        print('research done in %ds'%(int(t1-t0)))

    if inp == 'draw_matrices':
        #go in data/matrices/ and plot everything.
        files = glob.glob("data/matrices/*")
        for filename2 in files:
            M = return_adj_matrix(filename2)
            filename = filename2.split("data/matrices/")[1]
            sol = hard_solver([],M,len(M[0]), len(M[0]), mode = 'solution', problem = '3-2-5')
            name_img = 'img/blocking_gadgets/'+str(len(M[0]))+'_'+filename+'.png'
            G = igraph.Graph.Adjacency(M, mode = 'undirected')
            sol2 = [str(e) for e in sol] #no idea why but if i dont do it next line crashes
            col = ['red'*(i=='1')+'green'*(i=='0')+'gray'*(i=='2') for i in sol2]
            print(G, len(M[0]), col, name_img)
            igraph.plot(G, vertex_label=[i for i in range(len(M[0]))],vertex_color=col,target = name_img)