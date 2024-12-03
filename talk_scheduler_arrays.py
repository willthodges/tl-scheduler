import numpy as np
import csv, random, math

# read in teachers
teacher_arr = []
with open('teachers.csv', 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    next(reader)
    for row in reader:
        row  = ''.join(row).strip()
        teacher_arr.append(row)
teacher_arr = np.array(teacher_arr)

# read in talks
talk_dict = {}
with open('talks.csv', 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    next(reader)
    for row in reader:
        talk, advisor, primary_faculty = row
        talk = talk.strip().split(' ')
        talk = talk[1] + ' ' + talk[0].strip(',')
        advisor = advisor.strip()
        primary_faculty = primary_faculty.strip()
        talk_dict[talk] = (advisor, primary_faculty)

def pop_init(N_POP, N_ROOMS, N_SESSIONS):
    '''construct an inital population'''
    talk_pop, panel_pop = [], []
    leftover = N_ROOMS - (N_ROOMS * N_SESSIONS - len(talk_dict))
    if leftover == 0:
        leftover = N_ROOMS
    for _ in range(N_POP):
        # create random sample of talks
        talk_solution = random.sample([talk for talk in talk_dict], len(talk_dict))
        panel_solution = []
        for i in range(N_SESSIONS):
            if i != N_SESSIONS-1:
                # sample a random session
                session_new = random.sample(teacher_arr, N_ROOMS*3)
            else:
                session_new = random.sample(teacher_arr, leftover*3)
            # append each session to the solution
            panel_solution.extend(session_new)
        # append each solution to the population
        talk_pop.append(talk_solution)
        panel_pop.append(panel_solution)
    return talk_pop, panel_pop

def fitness(talk_solution, panel_solution, TEACHER_TALK_MAX, TEACHER_TALK_MAX_PENALTY, ADVISOR_REWARD, PRIMARY_FACULTY_REWARD):
    '''evaluate the fitness of a solution'''
    score = 0
    primary_faculty_score = 0
    teacher_talks_dict = {}
    for teacher in teacher_arr:
        teacher_talks_dict[teacher] = 0
    for teacher in panel_solution:
        teacher_talks_dict[teacher] += 1
        if teacher_talks_dict[teacher] > TEACHER_TALK_MAX:
            # penalty each time teacher has too many talks
            score += TEACHER_TALK_MAX_PENALTY
    panel_list = [panel_solution[i:i+3] for i in range(0, len(panel_solution), 3)]
    for panel_i in range(len(panel_list)):
        advisor = talk_dict[talk_solution[panel_i]][0]
        primary_faculty = talk_dict[talk_solution[panel_i]][1]
        for teacher in panel_list[panel_i]:
            if teacher_talks_dict[primary_faculty] <= TEACHER_TALK_MAX:
                if teacher == advisor:
                    # reward for advisor in talk
                    score += ADVISOR_REWARD
                if teacher == primary_faculty:
                    # reward for primary faculty in talk
                    score += PRIMARY_FACULTY_REWARD
                    primary_faculty_score += 1
    # convert score to unit interval where max score is when every talk has its advisor and primary faculty
    score = score/(len(talk_dict) * (ADVISOR_REWARD + PRIMARY_FACULTY_REWARD))
    primary_faculty_score = primary_faculty_score/len(talk_dict)
    return score, primary_faculty_score

def selection(talk_pop, panel_pop, scores_list, N_SELECTION):
    '''tournament selection'''
	# choose the highest score of N_SELECTION selections
    selection_i = np.randint(len(talk_pop))
    for i in np.randint(0, len(talk_pop), N_SELECTION-1):
        if scores_list[i][0] > scores_list[selection_i][0]:
            selection_i = i
    return [talk_pop[selection_i], panel_pop[selection_i]]

def crossover(p1, p2, R_CROSS, N_ROOMS):
    '''crossover two parents to create two children'''
    # children are copies of parents by default
    c1, c2 = p1.copy(), p2.copy()
    # check for recombination
    if random.random() < R_CROSS:
        # talk crossover
        pt = np.randint(1, len(p1[0])-2)
        c1[0] = p1[0][:pt] + p2[0][pt:]
        c2[0] = p2[0][:pt] + p1[0][pt:]
        # swap talks that appear more than once
        for talk_i in range(len(c1[0])):
            if c1[0].count(c1[0][talk_i]) > 1:
                avaliable = list(set(sorted(talk_dict)).symmetric_difference(set(c1[0])))
                c1[0][talk_i] = random.choice(avaliable)
        for talk_i in range(len(c2[0])):
            if c2[0].count(c2[0][talk_i]) > 1:
                avaliable = list(set(sorted(talk_dict)).symmetric_difference(set(c2[0])))
                c2[0][talk_i] = random.choice(avaliable)
        # panel crossover
        pt = np.randint(1, len(p1[1])-2)
        c1[1] = p1[1][:pt] + p2[1][pt:]
        c2[1] = p2[1][:pt] + p1[1][pt:]
        # c1[1] = p1[1][:pt*3] + p2[1][pt*3:]
        # c2[1] = p2[1][:pt*3] + p1[1][pt*3:]
        # swap teachers that appear more than once in a session
        session_list = [c1[1][i:i + N_ROOMS*3] for i in range(0, len(c1[1]), N_ROOMS*3)]
        for session_i in range(len(session_list)):
            for teacher_i in range(len(session_list[session_i])):
                if session_list[session_i].count(session_list[session_i][teacher_i]) > 1:
                    avaliable = list(set(teacher_arr).symmetric_difference(set(session_list[session_i])))
                    c1[1][session_i * N_ROOMS*3 + teacher_i] = random.choice(avaliable)
        session_list = [c2[1][i:i + N_ROOMS*3] for i in range(0, len(c2[1]), N_ROOMS*3)]
        for session_i in range(len(session_list)):
            for teacher_i in range(len(session_list[session_i])):
                if session_list[session_i].count(session_list[session_i][teacher_i]) > 1:
                    avaliable = list(set(teacher_arr).symmetric_difference(set(session_list[session_i])))
                    c2[1][session_i * N_ROOMS*3 + teacher_i] = random.choice(avaliable)
    return c1, c2

def mutation(talk_solution, panel_solution, R_TALKMUT, R_PANELMUT, N_ROOMS):
    '''mutation operator'''
    # talk mutation
    for talk_i in range(len(talk_solution)):
        if random.random() < R_TALKMUT:
            swap_i = random.randint(0, len(talk_solution)-1)
            talk_solution[talk_i], talk_solution[swap_i] = talk_solution[swap_i], talk_solution[talk_i]
    # panel mutation
    for panel_i in range(len(panel_solution)):
        if random.random() < R_PANELMUT:
            panel_solution[panel_i] = random.choice(teacher_arr)
    # swap teachers that appear more than once in a session
    session_list = [panel_solution[i:i + N_ROOMS*3] for i in range(0, len(panel_solution), N_ROOMS*3)]
    for session_i in range(len(session_list)):
        for teacher_i in range(len(session_list[session_i])):
            if session_list[session_i].count(session_list[session_i][teacher_i]) > 1:
                avaliable = list(set(teacher_arr).symmetric_difference(set(session_list[session_i])))
                panel_solution[session_i * N_ROOMS*3 + teacher_i] = random.choice(avaliable)

def out_file(talk_solution, panel_solution, score, primary_faculty_score, N_ROOMS, N_SESSIONS):
    '''Construct a solution csv'''
    with open('talk_schedule_solution.csv', 'w', newline='') as out_file:
        panel_list = [panel_solution[i:i+3] for i in range(0, len(panel_solution), 3)]
        for i in range(len(panel_list)):
            panel_list[i].insert(0, talk_solution[i])
        session_list = [panel_list[i:i + N_ROOMS] for i in range(0, len(panel_list), N_ROOMS)]
        writer = csv.writer(out_file)
        writer.writerow(['Score:', round(score, 3), 'Primary Faculty\nScore:', round(primary_faculty_score, 3)])
        # headers
        writer.writerow([''] + [f'Room {i}' for i in range(1, N_ROOMS+1)])
        for i in range(N_SESSIONS):
            dataline = ['Session ' + str(i+1)]
            for panel in session_list[i]:
                dataline.append('\n'.join(panel))
            writer.writerow(dataline)

def genetic_algorithm(N_POP, R_CROSS, R_TALKMUT, R_PANELMUT, N_SELECTION, N_ROOMS, N_SESSIONS, TEACHER_TALK_MAX, TEACHER_TALK_MAX_PENALTY, ADVISOR_REWARD, PRIMARY_FACULTY_REWARD):
    '''genetic algorithm main function'''
    # initial population
    talk_pop, panel_pop = pop_init(N_POP, N_ROOMS, N_SESSIONS)
    # keep track of best solution
    talk_best, panel_best = [], []
    best_score, best_primary_faculty_score = fitness(talk_pop[0], panel_pop[0], TEACHER_TALK_MAX, TEACHER_TALK_MAX_PENALTY, ADVISOR_REWARD, PRIMARY_FACULTY_REWARD)
    # keep track of overall best score
    with open('talk_schedule_solution.csv', 'r', newline='') as in_file:
        reader = csv.reader(in_file)
        reader_list = list(reader)
        if len(reader_list) == 0:
            overall_best_score = best_score
        else:
            overall_best_score = float(reader_list[0][1])
    # enumerate generations
    gen = 0
    while True:
        gen += 1
        # evaluate all candidates in the population
        scores_list = [fitness(talk_solution, panel_solution, TEACHER_TALK_MAX, TEACHER_TALK_MAX_PENALTY, ADVISOR_REWARD, PRIMARY_FACULTY_REWARD) for talk_solution, panel_solution in zip(talk_pop, panel_pop)]
        # check for new best solution
        for i in range(N_POP):
            if scores_list[i][0] > best_score:
                talk_best, panel_best, best_score, best_primary_faculty_score = talk_pop[i], panel_pop[i], scores_list[i][0], scores_list[i][1]
                print(f'>{gen}, score: {round(best_score, 3)}, PF score: {round(best_primary_faculty_score, 3)}')
            elif gen % 1000 == 0:
                print(f'>{gen}')
        # write best solution to file
        if best_score > overall_best_score:
            overall_best_score = best_score
            out_file(talk_best, panel_best, best_score, best_primary_faculty_score, N_ROOMS, N_SESSIONS)
        # select parents
        selected = [selection(talk_pop, panel_pop, scores_list, N_SELECTION) for _ in range(N_POP)]
        # create the next generation
        talk_children, panel_children = [], []
        for i in range(0, N_POP, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i+1]
            # crossover and mutation
            for talk_solution, panel_solution in crossover(p1, p2, R_CROSS, N_ROOMS):
                # mutation
                mutation(talk_solution, panel_solution, R_TALKMUT, R_PANELMUT, N_ROOMS)
                # store for next generation
                talk_children.append(talk_solution)
                panel_children.append(panel_solution)
        # replace population
        talk_pop, panel_pop = talk_children, panel_children

# population size (number of talks*10)
N_POP = len(talk_dict)*10
# crossover rate
R_CROSS = 0.9
# talk mutation rate (1/number of talks)
R_TALKMUT = 1/len(talk_dict)
# panel mutation rate (1/number of talks*3)
R_PANELMUT = 1/(len(talk_dict)*3)
# number of candidates drawn in selection (number of talks*0.3)
N_SELECTION = round(len(talk_dict)*0.3)
# number of rooms in a session
N_ROOMS = 5
# number of sessions
N_SESSIONS = math.ceil(len(talk_dict)/N_ROOMS)
# target max talks for a teacher
TEACHER_TALK_MAX = 11
# score penalty for going over target max talks
TEACHER_TALK_MAX_PENALTY = -1
# score reward for a talk having its advisor
ADVISOR_REWARD = 1
# score reward for a talk having its primary faculty
PRIMARY_FACULTY_REWARD = 3

# perform the genetic algorithm search
genetic_algorithm(N_POP, R_CROSS, R_TALKMUT, R_PANELMUT, N_SELECTION, N_ROOMS, N_SESSIONS, TEACHER_TALK_MAX, TEACHER_TALK_MAX_PENALTY, ADVISOR_REWARD, PRIMARY_FACULTY_REWARD)