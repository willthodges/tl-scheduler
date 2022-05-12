from numpy.random import randint
import csv, random, math

teacherList = []
with open('teachers.csv', 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    next(reader)
    for row in reader:
        row  = ''.join(row).strip()
        teacherList.append(row)

talkDict = {}
with open('talks.csv', 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    next(reader)
    for row in reader:
        (talk, advisor, primaryFaculty) = row
        talk = talk.strip()
        advisor = advisor.strip()
        primaryFaculty = primaryFaculty.strip()
        talkDict[talk] = (advisor, primaryFaculty)

def pop_init(n_pop, rooms, sessions):
    talkPop, panelPop = [], []
    leftover = rooms - (rooms*sessions - len(talkDict))
    if leftover == 0:
        leftover = rooms
    for _ in range(n_pop):
        # create random sample of talks
        talkSolution = random.sample([talk for talk in talkDict], len(talkDict))
        panelSolution = []
        for i in range(sessions):
            if i != sessions-1:
                # sample a random session
                sessionNew = random.sample(teacherList, rooms*3)
            else:
                sessionNew = random.sample(teacherList, leftover*3)
            # append each session to the solution
            panelSolution.extend(sessionNew)
        # append each solution to the population
        talkPop.append(talkSolution)
        panelPop.append(panelSolution)
    return [talkPop, panelPop]

def fitness(talkSolution, panelSolution, teacherTalkMax):
    score = 0
    teacherTalks = {}
    for teacher in teacherList:
        teacherTalks[teacher] = 0
    for teacher in panelSolution:
        teacherTalks[teacher] += 1
        if teacherTalks[teacher] > teacherTalkMax:
            score -= 1 # too many talks
    panelList = [panelSolution[i:i+3] for i in range(0, len(panelSolution), 3)]
    for panel_i in range(len(panelList)):
        advisor = talkDict[talkSolution[panel_i]][0]
        primaryFaculty = talkDict[talkSolution[panel_i]][1]
        for teacher in panelList[panel_i]:
            if teacherTalks[primaryFaculty] <= teacherTalkMax:
                if teacher == advisor:
                    score += 1 # advisor in talk
                if teacher == primaryFaculty:
                    score += 1 # primary faculty in talk
    score = score/(len(talkDict)*2)
    return score

def selection(talkPop, panelPop, scores, k):
	# choose the highest score of k selections
    selection_i = randint(len(talkPop))
    for i in randint(0, len(talkPop), k-1):
        if scores[i] > scores[selection_i]:
            selection_i = i
    return [talkPop[selection_i], panelPop[selection_i]]

# crossover two parents to create two children
def crossover(p1, p2, r_cross, rooms):
    # children are copies of parents by default
    c1, c2 = p1.copy(), p2.copy()
    # check for recombination
    if random.random() < r_cross:
        # talk crossover
        pt = randint(1, len(p1[0])-2)
        c1[0] = p1[0][:pt] + p2[0][pt:]
        c2[0] = p2[0][:pt] + p1[0][pt:]
        # swap talks that appear more than once
        for talk_i in range(len(c1[0])):
            if c1[0].count(c1[0][talk_i]) > 1:
                avaliable = list(set(sorted(talkDict)).symmetric_difference(set(c1[0])))
                c1[0][talk_i] = random.choice(avaliable)
        for talk_i in range(len(c2[0])):
            if c2[0].count(c2[0][talk_i]) > 1:
                avaliable = list(set(sorted(talkDict)).symmetric_difference(set(c2[0])))
                c2[0][talk_i] = random.choice(avaliable)
        # panel crossover
        pt = randint(1, len(p1[1])-2)
        c1[1] = p1[1][:pt] + p2[1][pt:]
        c2[1] = p2[1][:pt] + p1[1][pt:]
        # c1[1] = p1[1][:pt*3] + p2[1][pt*3:]
        # c2[1] = p2[1][:pt*3] + p1[1][pt*3:]
        # swap teachers that appear more than once in a session
        sessionList = [c1[1][i:i+rooms*3] for i in range(0, len(c1[1]), rooms*3)]
        for session_i in range(len(sessionList)):
            for teacher_i in range(len(sessionList[session_i])):
                if sessionList[session_i].count(sessionList[session_i][teacher_i]) > 1:
                    avaliable = list(set(teacherList).symmetric_difference(set(sessionList[session_i])))
                    c1[1][session_i*rooms*3 + teacher_i] = random.choice(avaliable)
        sessionList = [c2[1][i:i+rooms*3] for i in range(0, len(c2[1]), rooms*3)]
        for session_i in range(len(sessionList)):
            for teacher_i in range(len(sessionList[session_i])):
                if sessionList[session_i].count(sessionList[session_i][teacher_i]) > 1:
                    avaliable = list(set(teacherList).symmetric_difference(set(sessionList[session_i])))
                    c2[1][session_i*rooms*3 + teacher_i] = random.choice(avaliable)
    return [c1, c2]

def mutation(talkSolution, panelSolution, r_talkMut, r_panelMut, rooms):
    # talk mutation
    for talk_i in range(len(talkSolution)):
        if random.random() < r_talkMut:
            swap_i = random.randint(0, len(talkSolution)-1)
            talkSolution[talk_i], talkSolution[swap_i] = talkSolution[swap_i], talkSolution[talk_i]
    # panel mutation
    for panel_i in range(len(panelSolution)):
        if random.random() < r_panelMut:
            panelSolution[panel_i] = random.choice(teacherList)
    # swap teachers that appear more than once in a session
    sessionList = [panelSolution[i:i+rooms*3] for i in range(0, len(panelSolution), rooms*3)]
    for session_i in range(len(sessionList)):
        for teacher_i in range(len(sessionList[session_i])):
            if sessionList[session_i].count(sessionList[session_i][teacher_i]) > 1:
                avaliable = list(set(teacherList).symmetric_difference(set(sessionList[session_i])))
                panelSolution[session_i*rooms*3 + teacher_i] = random.choice(avaliable)

def out_file(talkSolution, panelSolution, score, rooms, sessions):
    with open('talk_schedule.csv', 'w', newline='') as out_file:
        panelList = [panelSolution[i:i+3] for i in range(0, len(panelSolution), 3)]
        for i in range(len(panelList)):
            panelList[i].insert(0, talkSolution[i])
        sessionList = [panelList[i:i+rooms] for i in range(0, len(panelList), rooms)]
        writer = csv.writer(out_file)
        writer.writerow(['score', score])
        # headers
        writer.writerow(['Session', 'Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5'])
        for i in range(sessions):
            dataline = ['Session ' + str(i+1)]
            for panel in sessionList[i]:
                dataline.append('\n'.join(panel))
            writer.writerow(dataline)

def genetic_algorithm(n_iter, n_pop, r_cross, r_talkMut, r_panelMut, k, rooms, sessions, teacherTalkMax):
    # initial population
    talkPop, panelPop = pop_init(n_pop, rooms, sessions)
    # keep track of best solution
    talkBest, panelBest, bestScore = 0, 0, fitness(talkPop[0], panelPop[0], teacherTalkMax)
    # keep track of overall best score
    with open('talk_schedule.csv', 'r', newline='') as in_file:
        reader = csv.reader(in_file)
        readerList = list(reader)
        if len(readerList) == 0:
            overallBestScore = 0
        else:
            overallBestScore = float(readerList[0][1])
    # enumerate generations
    for gen in range(n_iter):
        if gen % 1000 == 0:
            print(f'>{gen}')
        # evaluate all candidates in the population
        scores = [fitness(talkSolution, panelSolution, teacherTalkMax) for talkSolution, panelSolution in zip(talkPop, panelPop)]
        # check for new best solution
        for i in range(n_pop):
            if scores[i] > bestScore:
                talkBest, panelBest, bestScore = talkPop[i], panelPop[i], scores[i]
                print(f'>{gen}, new best: {round(bestScore, 3)}')
        # write best solution to file
        if bestScore > overallBestScore:
            overallBestScore = bestScore
            out_file(talkBest, panelBest, overallBestScore, rooms, sessions)
        # select parents
        selected = [selection(talkPop, panelPop, scores, k) for _ in range(n_pop)]
        # create the next generation
        talkChildren, panelChildren = [], []
        for i in range(0, n_pop, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i+1]
            # crossover and mutation
            for talkSolution, panelSolution in crossover(p1, p2, r_cross, rooms):
                # mutation
                mutation(talkSolution, panelSolution, r_talkMut, r_panelMut, rooms)
                # store for next generation
                talkChildren.append(talkSolution)
                panelChildren.append(panelSolution)
        # replace population
        talkPop, panelPop = talkChildren, panelChildren
    print('Done')

# define the total iterations
n_iter = 100000
# define the population size (talks*10)
n_pop = len(talkDict)*10
# crossover rate
r_cross = 0.9
# talk mutation rate (1/talks)
r_talkMut = 1/len(talkDict)
# panel mutation rate (1/talks*3)
r_panelMut = 1/(len(talkDict)*3)
# candidates drawn in selection (population size*0.03)
k = round(len(talkDict)*0.3)
# number of rooms in a session
rooms = 5
# number of sessions
sessions = math.ceil(len(talkDict)/rooms)
# target max talks for a teacher
teacherTalkMax = 12

# perform the genetic algorithm search
genetic_algorithm(n_iter, n_pop, r_cross, r_talkMut, r_panelMut, k, rooms, sessions, teacherTalkMax)

#session #
#first name, last name