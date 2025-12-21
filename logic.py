import networkx as nx
import numpy as np
import random
from config import *

## 1. Generate Social Network
def create_social_network(total_people, k, p):
    G = nx.watts_strogatz_graph(n=total_people, k=k, p=p)
    pos = nx.spring_layout(G, seed=42, k=0.15)
    return G, pos

## 2. Map networkx node positions to screen coordinates
def get_screen_coords(pos_dict):
    screen_coords = {}
    padding = 50
    xs = [x for x, y in pos_dict.values()]
    ys = [y for x, y in pos_dict.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    sim_width = WIDTH - SIDEBAR_WIDTH
    for node, (x, y) in pos_dict.items():
        norm_x = (x - min_x) / (max_x - min_x)
        norm_y = (y - min_y) / (max_y - min_y)
        screen_x = int(SIDEBAR_WIDTH + padding + norm_x * (sim_width - 2 * padding))
        screen_y = int(padding + norm_y * (HEIGHT - 2 * padding))
        screen_coords[node] = (screen_x, screen_y)
    return screen_coords


## 3. Initialize Population States
def initialize_population(G, initial_infected_count):
    for i in G.nodes():
        rand_age = random.random()
        if rand_age < PROB_CHILD: age = 'child'
        elif rand_age < PROB_CHILD + PROB_ADULT: age = 'adult'
        else: age = 'old'

        is_vaccinated = np.random.choice([True,False], p=[VACCINE_COVERAGE, 1-VACCINE_COVERAGE])
        uses_mask = np.random.choice([True,False], p=[MASK_COVERAGE, 1-MASK_COVERAGE])

        G.nodes[i]['state'] = STATE_SUSCEPTIBLE
        G.nodes[i]['age'] = age     
        G.nodes[i]['vaccinated'] = is_vaccinated
        G.nodes[i]['mask'] = uses_mask 
        G.nodes[i]['days_infected'] = 0
        G.nodes[i]['incubation_counter'] = 0

    initial_count = min(initial_infected_count, len(G.nodes()))
    initial_infected = random.sample(list(G.nodes()), initial_count)
    for node in initial_infected:
        G.nodes[node]['state'] = STATE_INFECTIOUS

## 4. Simulation Logic
def step_simulation(G, current_prob, incubation_period, min_dur, max_dur):
    newly_infected = []
    
    # A. Transmission
    infected_nodes = [n for n in G.nodes if G.nodes[n]['state'] == STATE_INFECTIOUS]
    for node in infected_nodes:
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if G.nodes[neighbor]['state'] == STATE_SUSCEPTIBLE:
                prob = current_prob
                if G.nodes[neighbor]['vaccinated']: prob *= (1-VACCINE_EFFICIENCY)
                if G.nodes[neighbor]['mask']: prob *= (1-MASK_EFFICACY)

                if random.random() < prob:
                    if neighbor not in newly_infected:
                        newly_infected.append(neighbor)

    for node in newly_infected:
        G.nodes[node]['state'] = STATE_EXPOSED


    # B. Progression
    for node in G.nodes():
        state = G.nodes[node]['state']
        if state == STATE_EXPOSED:
            G.nodes[node]['incubation_counter'] += 1
            if G.nodes[node]['incubation_counter'] >= incubation_period:
                G.nodes[node]['state'] = STATE_INFECTIOUS
        elif state == STATE_INFECTIOUS:
            G.nodes[node]['days_infected'] += 1
            days = G.nodes[node]['days_infected']
            if days > min_dur:
                age = G.nodes[node]['age']
                death_prob = DEATH_PROB_CHILD if age=='child' else (DEATH_PROB_ADULT if age=='adult' else DEATH_PROB_OLD)
                if random.random() < death_prob:
                    G.nodes[node]['state'] = STATE_DEAD
                    continue
            if days >= max_dur:
                G.nodes[node]['state'] = STATE_RECOVERED