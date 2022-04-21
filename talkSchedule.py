from numpy.random import randint
import csv, random, math

teacherSubject = {}
with open('teachers.csv', 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    next(reader)
    for row in reader:
        (teacher, subject) = row
        teacherSubject[teacher] = subject

talkDict = {}
with open('talks.csv', 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    next(reader)
    for row in reader:
        (talk, advisor, primaryFaculty, subject) = row
        talkDict[int(talk)] = (advisor, primaryFaculty, subject)

def pop_init(n_pop, rooms, sessions):
    talkPop = []
    panelPop = []
    leftover = rooms-(rooms*sessions-len(talkDict))
    if leftover == 0:
        leftover = rooms
    for _ in range(n_pop):
        # create random sample of talks
        talkSolution = random.sample([talk for talk in talkDict], len(talkDict))
        panelSolution = []
        for i in range(sessions):
            if i != sessions-1:
                # sample a random session
                sessionNew = random.sample((sorted(teacherSubject)), rooms*3)
            else:
                sessionNew = random.sample((sorted(teacherSubject)), leftover*3)
            # append each session to the solution
            panelSolution.extend(sessionNew)
        # append each solution to the population
        talkPop.append(talkSolution)
        panelPop.append(panelSolution)
    return [talkPop, panelPop]

def objective(talkPop, panelPop, teacherTalkMax):
    score = 0

    teacherTalks = {}
    for teacher in teacherSubject.keys():
        teacherTalks[teacher] = 0
    for teacher in panelPop:
        teacherTalks[teacher] += 1
        if teacherTalks[teacher] > teacherTalkMax:
            score -= 1 # too many talks

    for teacher in panelPop:
        advisor = talkDict[talkPop[math.floor(panelPop.index(teacher)/3)]][0]
        primaryFaculty = talkDict[talkPop[math.floor(panelPop.index(teacher)/3)]][1]
        subject = talkDict[talkPop[math.floor(panelPop.index(teacher)/3)]][2]

    for session in pop:
        for talk in session:
            advisor = talkDict[talk[0]][0]
            primaryFaculty = talkDict[talk[0]][1]
            subject = talkDict[talk[0]][2]
            subjectTeacher = False
            for teacher in talk[1:]:
                if teacher == advisor:
                    score += 1 # advisor in talk
                    # if advisor is also subject teacher, don't count both
                    continue
                # if primary faculty has too many talks, count score for subject teacher instead
                if teacherTalks[primaryFaculty] <= teacherTalkMax:
                    if teacher == primaryFaculty:
                        score += 1 # primary faculty in talk
                else:
                    if teacherSubject[teacher] == subject:
                        # only count one subject teacher
                        if subjectTeacher == False:
                            score += 0.5 # subject teacher in talk
                            subjectTeacher = True
    return score

def selection(pop, scores, k=3):
	# choose the highest score of k selections
    selectionIndex = randint(len(pop))
    for i in randint(0, len(pop), k-1):
        if scores[i] > scores[selectionIndex]:
            selectionIndex = i
    return pop[selectionIndex]

# crossover two parents to create two children
def crossover(p1, p2, r_cross):
    # children are copies of parents by default
    c1, c2 = p1.copy(), p2.copy()

    # check for recombination
    if random.random() < r_cross:
        sessionIndex = 0
        for session in zip(p1, p2):
            # create list of teachers in each session
            p1Teachers, p2Teachers = [], []
            for talk in session[0]:
                for teacher in talk[1:]:
                    p1Teachers.append(teacher)
            for talk in session[1]:
                for teacher in talk[1:]:
                    p2Teachers.append(teacher)

            # find unique teachers in both sessions and their indices
            combinedTeachers = p1Teachers + p2Teachers
            p1Unique, p2Unique, p1Index, p2Index = [], [], [], []
            for teacher in p1Teachers:
                if combinedTeachers.count(teacher) == 1:
                    p1Unique.append(teacher)
                    p1Index.append(p1Teachers.index(teacher))
            for teacher in p2Teachers:
                if combinedTeachers.count(teacher) == 1:
                    p2Unique.append(teacher)
                    p2Index.append(p2Teachers.index(teacher))
            # make lists same length
            length = min(len(p1Unique), len(p2Unique))
            if length == 0:
                continue
            p1Unique, p2Unique, p1Index, p2Index = p1Unique[:length], p2Unique[:length], p1Index[:length], p2Index[:length]

            # perform crossover
            pt = random.randint(0, len(p1Unique)-1)
            c1Replace = p1Unique[:pt] + p2Unique[pt:]
            c2Replace = p2Unique[:pt] + p1Unique[pt:]

            teacherIndex = 0
            for i in range(len(p1[sessionIndex])):
                for j in range(1, len(p1[sessionIndex][i])):
                    if teacherIndex in p1Index:
                        c1[sessionIndex][i][j] = c1Replace[p1Index.index(teacherIndex)]
                    if teacherIndex in p2Index:
                        c2[sessionIndex][i][j] = c2Replace[p2Index.index(teacherIndex)]
                    teacherIndex += 1

            sessionIndex += 1
    return [c1, c2]

# 🍝😭
def mutation(solution, r_mut):
    for i in range(len(talkDict)):
        if random.random() < r_mut:
            t1 = solution[math.ceil((i+1)/5)-1][i-math.floor(i/5)*5][0]
            j = random.randint(0, len(talkDict)-1)
            t2 = solution[math.ceil((j+1)/5)-1][j-math.floor(j/5)*5][0]
            solution[math.ceil((i+1)/5)-1][i-math.floor(i/5)*5][0], solution[math.ceil((j+1)/5)-1][j-math.floor(j/5)*5][0] = t2, t1

    for i in range(len(talkDict)*3):
        if random.random() < r_mut:
            t1 = solution[math.ceil((i+1)/15)-1][math.floor(i/3)-math.floor(i/15)*5][i-math.floor(i/3)*3+1]
            j = random.randint(0, len(talkDict)*3-1)
            t2 = solution[math.ceil((j+1)/15)-1][math.floor(j/3)-math.floor(j/15)*5][j-math.floor(j/3)*3+1]
            solution[math.ceil((i+1)/15)-1][math.floor(i/3)-math.floor(i/15)*5][i-math.floor(i/3)*3+1], solution[math.ceil((j+1)/15)-1][math.floor(j/3)-math.floor(j/15)*5][j-math.floor(j/3)*3+1] = t2, t1

<<<<<<< HEAD
def genetic_algorithm(n_iter, n_pop, r_cross, r_mut, rooms, sessions, teacherTalkMax):
=======
def genetic_algorithm(n_iter, n_pop, r_cross, r_mut, roomsNum, sessions, teacherTalkMax):
>>>>>>> 301ed589cdb7f6fa8ab07b9251ebbd12c5987542
    # initial population
    pop = pop_init(n_pop, rooms, sessions)
    # keep track of best solution
    best, best_eval = 0, objective(pop[0], teacherTalkMax)
    # enumerate generations
    for gen in range(n_iter):
        # evaluate all candidates in the population
        scores = [objective(solution, teacherTalkMax) for solution in pop]
        print(scores)
        # check for new best solution
        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]
                print(f'>{gen}, new best: {scores[i]}')
        # select parents
        selected = [selection(pop, scores) for _ in range(n_pop)]
        # create the next generation
        children = []
        for i in range(0, n_pop, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i+1]
            # crossover and mutation
            for solution in crossover(p1, p2, r_cross):
                # mutation
                mutation(solution, r_mut)
                # store for next generation
                children.append(solution)
        # replace population
        pop = children
    return [best, best_eval]

# define the total iterations
n_iter = 100
# define the population size
n_pop = 100
# crossover rate
r_cross = 0.9
# mutation rate
r_mut = 0.05
# number of rooms in a session
rooms = 5
# number of sessions
sessions = math.ceil(len(talkDict)/rooms)
# target max talks for a teacher
teacherTalkMax = 18

# perform the genetic algorithm search
<<<<<<< HEAD
# best, score = genetic_algorithm(n_iter, n_pop, r_cross, r_mut, rooms, sessions, teacherTalkMax)
# print('Done')
# print(score)
=======
best, score = genetic_algorithm(n_iter, n_pop, r_cross, r_mut, roomsNum, sessions, teacherTalkMax)
print('Done')
print(score)
>>>>>>> 301ed589cdb7f6fa8ab07b9251ebbd12c5987542

# third teacher unique subject
# primary faculty 
# teacher max? switch to subject teacher?

# TO DO
# make talks and teachers seperate lists
# recombine entire talk and teacher list
# if teacher appears twice in groups of 15, switch for a random unique teacher
# mutate both lists the same way