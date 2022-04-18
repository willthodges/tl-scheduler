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

def pop_init(n_pop, roomsNum, sessions):
    pop = []
    for i in range(n_pop):
        solution = []
        # create random sample of talks
        talkRandom = random.sample([talk for talk in talkDict], len(talkDict))
        for i in range(sessions):
            if len(talkRandom) >= roomsNum:
            # create list of three teachers per panel
                sessionNew = random.sample((sorted(teacherSubject)), roomsNum*3)
            # if there are less talks than rooms, only assign teachers to remaining talks
            else:
                sessionNew = random.sample((sorted(teacherSubject)), len(talkRandom)*3)
            # split list into sublists containing three teachers
            sessionNew = [sessionNew[i:i+3] for i in range(0, len(sessionNew), 3)]

            # for every panel choose a random talk to append
            for panel in sessionNew:
                talk = random.choice(talkRandom)
                panel.insert(0, talk)
                talkRandom.remove(talk)
            # append each session to the solution
            solution.append(sessionNew)
        # append each solution to the population
        pop.append(solution)
    return pop

def objective(pop, teacherTalkMax):
    score = 0
    teacherTalks = {}
    for teacher in teacherSubject.keys():
        teacherTalks[teacher] = 0
    for session in pop:
        for talk in session:
            for teacher in talk[1:]:
                teacherTalks[teacher] += 1
                if teacherTalks[teacher] > teacherTalkMax:
                    score -= 1 # too many talks

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
                            score += 1 # subject teacher in talk
                            subjectTeacher = True
    return score

def selection(pop, scores, k=3):
	# choose the highest score of k selections
    selection_ix = randint(len(pop))
    for ix in randint(0, len(pop), k-1):
        if scores[ix] > scores[selection_ix]:
            selection_ix = ix
        return pop[selection_ix]

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
            p1Unique, p2Unique, p1Index, p2Index = p1Unique[:length], p2Unique[:length], p1Index[:length], p2Index[:length]

            # perform crossover
            pt = randint(len(p1Unique)-1)
            c1Replace = p1Unique[:pt] + p2Unique[pt:]
            c2Replace = p2Unique[:pt] + p1Unique[pt:]

            # 🍝
            teacherIndex = 0
            for i in range(len(p1[sessionIndex])):
                for j in range(1, len(p1[sessionIndex][i])):
                    if teacherIndex in p1Index:
                        c1[sessionIndex][i][j] = c1Replace[p1Index.index(teacherIndex)]
                    if teacherIndex in p2Index:
                        c2[sessionIndex][i][j] = c2Replace[p2Index.index(teacherIndex)]
                    teacherIndex += 1

            sessionIndex += 1
    return [p1, c1]

def genetic_algorithm():
    # inital population
    pop = pop_init(n_pop)
    # keep track of best solution
    best, best_eval = 0, objective
    # enumerate generations
    for gen in range(n_iter):
        # evaluate all solutions in the population
        scores = [objective(solution, teacherTalkMax) for solution in pop]
        selected = [selection(pop, scores) for _ in range(n_pop)]
        print(selected)

# define the total iterations
n_iter = 100
# define the population size
n_pop = 100
# crossover rate
r_cross = 0.9
# mutation rate
# r_mut = 1.0/float(n_bits)
# number of rooms in a session
roomsNum = 5
# number of sessions
sessions = math.ceil(len(talkDict)/roomsNum)
# target max talks for a teacher
teacherTalkMax = 18

# # perform the genetic algorithm search
# best, score = genetic_algorithm(onemax, n_bits, n_iter, n_pop, r_cross, r_mut)
# print('Done!')
# print('f(%s) = %f' % (best, score))


# popInit = pop_init()
# score = objective(popInit)
# # print(popInit)
# print(f'Score: {score} out of {len(talkDict)*2} ({round((score/(len(talkDict)*2))*100)}%)')

# third teacher unique subject
# primary faculty 
# teacher max? switch to subject teacher?