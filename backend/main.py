import random

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from os import environ

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

winner_points = 10
both_cooperate_points = 3
both_betray_points = 2
loser_points = 0

enemy_strategy = 0
# 0 - Random
# 1 - Always Cooperate
# 2 - Always Defect
# 3 - Tit for Tat (First Cooperate)
# 4 - Suspicious Tit for Tat (First Defect)
# 5 - Imperfect TFT (Imitates opponent's last move with high, but less than one, probability)
# 6 - Pavlov (Cooperates if it and its opponent moved alike in previous move and defects if they moved differently)

possible_enemies = [
    ["0", "Random"],
    ["1", "Always Cooperate"],
    ["2", "Always Defect"],
    ["3", "Tit for tat"],
    ["4", "Suspicious Tit for Tat"],
    ["5", "Imperfect TFT"],
    ["6", "Pavlov "]
]

population_size = 100  # Should be even
turns_in_a_game = 100
generations_to_do = 100

is_learning = False
generations_done = 0

best_strategy = []


# Initialize solution table with random tactic
def randomize_table():
    table = []
    for i in range(turns_in_a_game):  # For every move in tactic randomize it
        if random.randint(0, 1) == 0:
            table.append(True)  # Cooperate
        else:
            table.append(False)  # Defect
    return table


# Calculate the points of 2 players basing on their moves and the reward values
def calculate_points(player1, player2):
    player1score = 0
    player2score = 0
    for i in range(turns_in_a_game):
        if player1[i] and player2[i]:  # Both players cooperate
            player1score += both_cooperate_points
            player2score += both_cooperate_points
        elif player1[i] and not player2[i]:  # First player cooperates, second defects
            player1score += loser_points
            player2score += winner_points
        elif not player1[i] and player2[i]:  # First player defects, second cooperates
            player1score += winner_points
            player2score += loser_points
        elif not player1[i] and not player2[i]:  # Both players defect
            player1score += both_betray_points
            player2score += both_betray_points
    return player1score, player2score


# Calculate what the enemy is doing
def calculate_enemy_strategy(enemy, player):
    if enemy_strategy == 0:  # Random
        enemy_table = randomize_table()
        for i in range(population_size):
            enemy.append([])
            for j in range(turns_in_a_game):
                enemy[i].append(enemy_table[j])
    elif enemy_strategy == 1:  # Always Cooperate
        for i in range(population_size):
            enemy.append([])
            for j in range(turns_in_a_game):
                enemy[i].append(True)
    elif enemy_strategy == 2:  # Always Betray
        for i in range(population_size):
            enemy.append([])
            for j in range(turns_in_a_game):
                enemy[i].append(False)
    elif enemy_strategy == 3:  # Tit for Tat
        for i in range(population_size):
            enemy.append([])
            enemy[i].append(True)
            for j in range(1, turns_in_a_game):
                enemy[i].append(player[i][j - 1])
    elif enemy_strategy == 4:  # Suspicious Tit for Tat
        for i in range(population_size):
            enemy.append([])
            enemy[i].append(False)
            for j in range(1, turns_in_a_game):
                enemy[i].append(player[i][j - 1])
    elif enemy_strategy == 5:  # Imperfect TFT
        for i in range(population_size):
            enemy.append([])
            enemy[i].append(True)
            for j in range(1, turns_in_a_game):
                if random.randint(0, 9) > 1:
                    enemy[i].append(player[i][j - 1])
                else:
                    enemy[i].append(not player[i][j - 1])
    elif enemy_strategy == 6:  # Pavlov
        for i in range(population_size):
            enemy.append([])
            enemy[i].append(True)
            for j in range(1, turns_in_a_game):
                if enemy[i][j - 1] == player[i][j - 1]:
                    enemy[i].append(True)
                else:
                    enemy[i].append(False)


# Calculate enemy strategy for the final battle
def enemy_for_final_battle(enemy, player):
    if enemy_strategy == 0:  # Random
        enemy_table = randomize_table()
        for i in range(turns_in_a_game):
            enemy.append(enemy_table[i])
    elif enemy_strategy == 1:  # Always Cooperate
        for i in range(turns_in_a_game):
            enemy.append(True)
    elif enemy_strategy == 2:  # Always Betray
        for i in range(turns_in_a_game):
            enemy.append(False)
    elif enemy_strategy == 3:  # Tit for tat
        enemy.append(True)
        for i in range(1, turns_in_a_game):
            enemy.append(player[i - 1])
    elif enemy_strategy == 4:  # Suspicious Tit for Tat
        enemy.append(False)
        for i in range(1, turns_in_a_game):
            enemy.append(player[i - 1])
    elif enemy_strategy == 5:  # Imperfect TFT
        enemy.append(True)
        for i in range(1, turns_in_a_game):
            if random.randint(0, 9) > 1:
                enemy.append(player[i - 1])
            else:
                enemy.append(not player[i - 1])
    elif enemy_strategy == 6:  # Pavlov
        enemy.append(True)
        for i in range(1, turns_in_a_game):
            if enemy[i - 1] == player[i - 1]:
                enemy.append(True)
            else:
                enemy.append(False)


# Find_best_strategy
def find_best_strategy():
    global is_learning, generations_to_do
    global generations_done  # Count how many generations there were
    generations_done = 0

    player = []  # Table for finding the best strategy
    enemy = []  # Table for enemies moves in response to player's moves

    for i in range(population_size):
        player.append(randomize_table())  # Randomize the table of the tactics to have something to begin with

    # Calculate, what the enemy is going to do
    calculate_enemy_strategy(enemy, player)

    # Population cycle
    generations_left_to_do = generations_to_do
    while generations_left_to_do > 0:  # While there is still time to learn
        # Calculate the points of every player's and enemy's member
        points = [[], []]  # Table for difference of player's and enemy's points and the amount of player's points
        for i in range(population_size):
            p, e = calculate_points(player[i], enemy[i])  # Calculate points of every member of the population
            d = p - e  # Calculate the difference of the points
            points[0].append(d)  # Save the difference
            points[1].append(p)  # and the player's points to be used in tournament comparisons

        playertemp = []  # Table to keep better half temporarily
        # Pick half of the population by binary tournament
        for i in range(int(population_size / 2)):
            playertemp.append([])
            if points[0][i] > points[0][i + int(population_size / 2)]:  # First wins by greater difference
                for j in range(turns_in_a_game):
                    playertemp[i].append(player[i][j])  # Pick and save i-th member strategy
            elif points[0][i] == points[0][i + int(population_size / 2)] \
                    and points[1][i] >= points[1][i + int(population_size / 2)]:
                # First wins by having greater score (or is the same and can choose either)
                for j in range(turns_in_a_game):
                    playertemp[i].append(player[i][j])  # Pick and save i-th member strategy
            else:  # Second one wins by having greater difference or more points
                for j in range(turns_in_a_game):
                    playertemp[i].append(player[i + int(population_size / 2)][j])
                    # Pick and save (i+population_size/2)-th member strategy

        # Now put them back into the original population
        for i in range(int(population_size / 2)):
            for j in range(turns_in_a_game):
                player[i][j] = playertemp[i][j]

        # Now create another half of the population randomly mixing the members of the winning half
        for i in range(int(population_size / 2), population_size):
            parent1 = random.randint(0, int(population_size / 2))
            parent2 = random.randint(0, int(population_size / 2))
            for j in range(turns_in_a_game):  # For every move decide from which parent it is taken
                if random.randint(0, 1) == 0:  # This move is taken from first parent
                    player[i][j] = player[parent1][j]
                else:  # This move is taken from the second parent
                    player[i][j] = player[parent2][j]
            # Randomize one cell
            cell_to_change = random.randint(0, turns_in_a_game - 1)
            player[i][cell_to_change] = not player[i][cell_to_change]

        # Calculate, what the enemy is going to do
        calculate_enemy_strategy(enemy, player)

        # Now a new population is ready for the next cycle
        generations_left_to_do -= 1
        generations_done += 1

    # Pick the best strategy after all the learning
    global best_strategy
    best_strategy = []
    for i in range(turns_in_a_game):
        best_strategy.append(player[0][i])
    initialb, initiale = calculate_points(best_strategy, enemy[0])
    best_difference = initialb - initiale
    best_points = initialb

    # Compare strategy to every member of population and choose the best
    # (the biggest difference & highest score)
    for i in range(1, population_size):
        p, e = calculate_points(player[i], enemy[i])
        d = p - e  # difference of the points

        if d > best_difference:  # Change the strategy if the difference is better with the new one
            for j in range(turns_in_a_game):
                best_strategy[j] = player[i][j]
                best_difference = d
                best_points = p
        elif d == best_difference and p > best_points:
            # Change the strategy if the differences are the same, but the new one is higher score
            for j in range(turns_in_a_game):
                best_strategy[j] = player[i][j]
                best_difference = d
                best_points = p
        # Else don't change, cause the strategy is the same or worse
    is_learning = False


@app.get("/develop-strategy/possible-enemies", response_class=JSONResponse)
async def get_possible_enemies():
    global possible_enemies
    return JSONResponse(content=possible_enemies)


@app.get("/develop-strategy/start/{enemy_id}/{population_size_par}/{turns_in_a_game_par}/{generations_to_do_par}"
         "/{points_for_winner}/{points_for_loser}/{points_both_betray}/{points_both_cooperate}")
async def develop_strategy(enemy_id: int, population_size_par: int,
                           turns_in_a_game_par: int, generations_to_do_par: int,
                           points_for_winner: int, points_for_loser: int,
                           points_both_betray: int, points_both_cooperate: int,
                           background_tasks: BackgroundTasks):
    global is_learning
    if is_learning:
        return JSONResponse(content=1)
    global enemy_strategy
    global population_size
    global turns_in_a_game
    global generations_to_do
    enemy_strategy = enemy_id
    population_size = population_size_par
    turns_in_a_game = turns_in_a_game_par
    generations_to_do = generations_to_do_par
    global winner_points
    global loser_points
    global both_cooperate_points
    global both_betray_points
    winner_points = points_for_winner
    loser_points = points_for_loser
    both_cooperate_points = points_both_cooperate
    both_betray_points = points_both_betray
    is_learning = True
    background_tasks.add_task(find_best_strategy)
    return JSONResponse(content=0)


@app.get("/develop-strategy/check-progress")
async def check_developing_progress():
    global is_learning
    if is_learning:
        return JSONResponse(content=int((generations_done / generations_to_do) * 100))
    else:
        return JSONResponse(content=100)


@app.get("/develop-strategy/get-result")
async def get_strategy_result():
    global is_learning
    if not is_learning:
        global best_strategy
        return JSONResponse(content=best_strategy)
    else:
        return {}


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=environ.get("PORT", 5000))
