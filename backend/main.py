import random

from os import environ

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://prisoners-dilemma.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WINNER_POINTS = 10
BOTH_COOPERATE_POINTS = 3
BOTH_BETRAY_POINTS = 2
LOSER_POINTS = 0

ENEMY_STRATEGY = 0
# 0 - Random
# 1 - Always Cooperate
# 2 - Always Defect
# 3 - Tit for Tat (First Cooperate)
# 4 - Suspicious Tit for Tat (First Defect)
# 5 - Imperfect TFT (Imitates opponent's last move with high, but less than one, probability)
# 6 - Pavlov (Cooperates if it and its opponent moved alike in previous move and defects if they moved differently)

POSSIBLE_ENEMIES = [
    ["0", "Random"],
    ["1", "Always Cooperate"],
    ["2", "Always Defect"],
    ["3", "Tit for tat"],
    ["4", "Suspicious Tit for Tat"],
    ["5", "Imperfect TFT"],
    ["6", "Pavlov "]
]

POPULATION_SIZE = 100  # Should be even
TURNS_IN_A_GAME = 100
GENERATIONS_TO_DO = 100

IS_LEARNING = False
GENERATIONS_DONE = 0

BEST_STRATEGY = []


# Initialize solution table with random tactic
def randomize_table():
    table = []
    for i in range(TURNS_IN_A_GAME):  # For every move in tactic randomize it
        if random.randint(0, 1) == 0:
            table.append(True)  # Cooperate
        else:
            table.append(False)  # Defect
    return table


# Calculate the points of 2 players basing on their moves and the reward values
def calculate_points(player1, player2):
    player1score = 0
    player2score = 0
    for i in range(TURNS_IN_A_GAME):
        if player1[i] and player2[i]:  # Both players cooperate
            player1score += BOTH_COOPERATE_POINTS
            player2score += BOTH_COOPERATE_POINTS
        elif player1[i] and not player2[i]:  # First player cooperates, second defects
            player1score += LOSER_POINTS
            player2score += WINNER_POINTS
        elif not player1[i] and player2[i]:  # First player defects, second cooperates
            player1score += WINNER_POINTS
            player2score += LOSER_POINTS
        elif not player1[i] and not player2[i]:  # Both players defect
            player1score += BOTH_BETRAY_POINTS
            player2score += BOTH_BETRAY_POINTS
    return player1score, player2score


# Calculate what the enemy is doing
def calculate_enemy_strategy(enemy, player):
    if ENEMY_STRATEGY == 0:  # Random
        enemy_table = randomize_table()
        for i in range(POPULATION_SIZE):
            enemy.append([])
            for j in range(TURNS_IN_A_GAME):
                enemy[i].append(enemy_table[j])
    elif ENEMY_STRATEGY == 1:  # Always Cooperate
        for i in range(POPULATION_SIZE):
            enemy.append([])
            for j in range(TURNS_IN_A_GAME):
                enemy[i].append(True)
    elif ENEMY_STRATEGY == 2:  # Always Betray
        for i in range(POPULATION_SIZE):
            enemy.append([])
            for j in range(TURNS_IN_A_GAME):
                enemy[i].append(False)
    elif ENEMY_STRATEGY == 3:  # Tit for Tat
        for i in range(POPULATION_SIZE):
            enemy.append([])
            enemy[i].append(True)
            for j in range(1, TURNS_IN_A_GAME):
                enemy[i].append(player[i][j - 1])
    elif ENEMY_STRATEGY == 4:  # Suspicious Tit for Tat
        for i in range(POPULATION_SIZE):
            enemy.append([])
            enemy[i].append(False)
            for j in range(1, TURNS_IN_A_GAME):
                enemy[i].append(player[i][j - 1])
    elif ENEMY_STRATEGY == 5:  # Imperfect TFT
        for i in range(POPULATION_SIZE):
            enemy.append([])
            enemy[i].append(True)
            for j in range(1, TURNS_IN_A_GAME):
                if random.randint(0, 9) > 1:
                    enemy[i].append(player[i][j - 1])
                else:
                    enemy[i].append(not player[i][j - 1])
    elif ENEMY_STRATEGY == 6:  # Pavlov
        for i in range(POPULATION_SIZE):
            enemy.append([])
            enemy[i].append(True)
            for j in range(1, TURNS_IN_A_GAME):
                if enemy[i][j - 1] == player[i][j - 1]:
                    enemy[i].append(True)
                else:
                    enemy[i].append(False)


# Calculate enemy strategy for the final battle
def enemy_for_final_battle(enemy, player):
    if ENEMY_STRATEGY == 0:  # Random
        enemy_table = randomize_table()
        for i in range(TURNS_IN_A_GAME):
            enemy.append(enemy_table[i])
    elif ENEMY_STRATEGY == 1:  # Always Cooperate
        for i in range(TURNS_IN_A_GAME):
            enemy.append(True)
    elif ENEMY_STRATEGY == 2:  # Always Betray
        for i in range(TURNS_IN_A_GAME):
            enemy.append(False)
    elif ENEMY_STRATEGY == 3:  # Tit for tat
        enemy.append(True)
        for i in range(1, TURNS_IN_A_GAME):
            enemy.append(player[i - 1])
    elif ENEMY_STRATEGY == 4:  # Suspicious Tit for Tat
        enemy.append(False)
        for i in range(1, TURNS_IN_A_GAME):
            enemy.append(player[i - 1])
    elif ENEMY_STRATEGY == 5:  # Imperfect TFT
        enemy.append(True)
        for i in range(1, TURNS_IN_A_GAME):
            if random.randint(0, 9) > 1:
                enemy.append(player[i - 1])
            else:
                enemy.append(not player[i - 1])
    elif ENEMY_STRATEGY == 6:  # Pavlov
        enemy.append(True)
        for i in range(1, TURNS_IN_A_GAME):
            if enemy[i - 1] == player[i - 1]:
                enemy.append(True)
            else:
                enemy.append(False)


# Find_best_strategy
def find_best_strategy():
    global IS_LEARNING
    global GENERATIONS_DONE  # Count how many generations there were
    GENERATIONS_DONE = 0

    player = []  # Table for finding the best strategy
    enemy = []  # Table for enemies moves in response to player's moves

    for i in range(POPULATION_SIZE):
        player.append(randomize_table())  # Randomize the table of the tactics to have something to begin with

    # Calculate, what the enemy is going to do
    calculate_enemy_strategy(enemy, player)

    # Population cycle
    generations_left_to_do = GENERATIONS_TO_DO
    while generations_left_to_do > 0:  # While there is still time to learn
        # Calculate the points of every player's and enemy's member
        points = [[], []]  # Table for difference of player's and enemy's points and the amount of player's points
        for i in range(POPULATION_SIZE):
            p, e = calculate_points(player[i], enemy[i])  # Calculate points of every member of the population
            d = p - e  # Calculate the difference of the points
            points[0].append(d)  # Save the difference
            points[1].append(p)  # and the player's points to be used in tournament comparisons

        playertemp = []  # Table to keep better half temporarily
        # Pick half of the population by binary tournament
        for i in range(int(POPULATION_SIZE / 2)):
            playertemp.append([])
            if points[0][i] > points[0][i + int(POPULATION_SIZE / 2)]:  # First wins by greater difference
                for j in range(TURNS_IN_A_GAME):
                    playertemp[i].append(player[i][j])  # Pick and save i-th member strategy
            elif points[0][i] == points[0][i + int(POPULATION_SIZE / 2)] \
                    and points[1][i] >= points[1][i + int(POPULATION_SIZE / 2)]:
                # First wins by having greater score (or is the same and can choose either)
                for j in range(TURNS_IN_A_GAME):
                    playertemp[i].append(player[i][j])  # Pick and save i-th member strategy
            else:  # Second one wins by having greater difference or more points
                for j in range(TURNS_IN_A_GAME):
                    playertemp[i].append(player[i + int(POPULATION_SIZE / 2)][j])
                    # Pick and save (i+population_size/2)-th member strategy

        # Now put them back into the original population
        for i in range(int(POPULATION_SIZE / 2)):
            for j in range(TURNS_IN_A_GAME):
                player[i][j] = playertemp[i][j]

        # Now create another half of the population randomly mixing the members of the winning half
        for i in range(int(POPULATION_SIZE / 2), POPULATION_SIZE):
            parent1 = random.randint(0, int(POPULATION_SIZE / 2))
            parent2 = random.randint(0, int(POPULATION_SIZE / 2))
            for j in range(TURNS_IN_A_GAME):  # For every move decide from which parent it is taken
                if random.randint(0, 1) == 0:  # This move is taken from first parent
                    player[i][j] = player[parent1][j]
                else:  # This move is taken from the second parent
                    player[i][j] = player[parent2][j]
            # Randomize one cell
            cell_to_change = random.randint(0, TURNS_IN_A_GAME - 1)
            player[i][cell_to_change] = not player[i][cell_to_change]

        # Calculate, what the enemy is going to do
        calculate_enemy_strategy(enemy, player)

        # Now a new population is ready for the next cycle
        generations_left_to_do -= 1
        GENERATIONS_DONE += 1

    # Pick the best strategy after all the learning
    global BEST_STRATEGY
    BEST_STRATEGY = []
    for i in range(TURNS_IN_A_GAME):
        BEST_STRATEGY.append(player[0][i])
    initialb, initiale = calculate_points(BEST_STRATEGY, enemy[0])
    best_difference = initialb - initiale
    best_points = initialb

    # Compare strategy to every member of population and choose the best
    # (the biggest difference & highest score)
    for i in range(1, POPULATION_SIZE):
        p, e = calculate_points(player[i], enemy[i])
        d = p - e  # difference of the points

        if d > best_difference:  # Change the strategy if the difference is better with the new one
            for j in range(TURNS_IN_A_GAME):
                BEST_STRATEGY[j] = player[i][j]
                best_difference = d
                best_points = p
        elif d == best_difference and p > best_points:
            # Change the strategy if the differences are the same, but the new one is higher score
            for j in range(TURNS_IN_A_GAME):
                BEST_STRATEGY[j] = player[i][j]
                best_difference = d
                best_points = p
        # Else don't change, cause the strategy is the same or worse
    IS_LEARNING = False


@app.get("/develop-strategy/possible-enemies", response_class=JSONResponse)
async def get_possible_enemies():
    return JSONResponse(content=POSSIBLE_ENEMIES)


@app.get("/develop-strategy/start/{enemy_id}/{population_size_par}/{turns_in_a_game_par}/{generations_to_do_par}"
         "/{points_for_winner}/{points_for_loser}/{points_both_betray}/{points_both_cooperate}")
async def develop_strategy(enemy_id: int, population_size_par: int,
                           turns_in_a_game_par: int, generations_to_do_par: int,
                           points_for_winner: int, points_for_loser: int,
                           points_both_betray: int, points_both_cooperate: int,
                           background_tasks: BackgroundTasks):
    global IS_LEARNING
    if IS_LEARNING:
        return JSONResponse(content=1)
    global ENEMY_STRATEGY
    global POPULATION_SIZE
    global TURNS_IN_A_GAME
    global GENERATIONS_TO_DO
    ENEMY_STRATEGY = enemy_id
    POPULATION_SIZE = population_size_par
    TURNS_IN_A_GAME = turns_in_a_game_par
    GENERATIONS_TO_DO = generations_to_do_par
    global WINNER_POINTS
    global LOSER_POINTS
    global BOTH_COOPERATE_POINTS
    global BOTH_BETRAY_POINTS
    WINNER_POINTS = points_for_winner
    LOSER_POINTS = points_for_loser
    BOTH_COOPERATE_POINTS = points_both_cooperate
    BOTH_BETRAY_POINTS = points_both_betray
    IS_LEARNING = True
    background_tasks.add_task(find_best_strategy)
    return JSONResponse(content=0)


@app.get("/develop-strategy/check-progress")
async def check_developing_progress():
    if IS_LEARNING:
        return JSONResponse(content=int((GENERATIONS_DONE / GENERATIONS_TO_DO) * 100))
    return JSONResponse(content=100)


@app.get("/develop-strategy/get-result")
async def get_strategy_result():
    if not IS_LEARNING:
        return JSONResponse(content=BEST_STRATEGY)
    return {}


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=int(environ.get("PORT", 5000)))
