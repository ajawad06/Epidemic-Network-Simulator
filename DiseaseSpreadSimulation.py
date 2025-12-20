import pygame, sys, math, random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

history = {
    "S": [],
    "E": [],
    "I": [],
    "R": [],
    "D": []
}


###### 1. VARIABLES and CONFIGURATIONS ######

# Pygame Display Settings
WIDTH, HEIGHT = 1000, 800
FPS = 30                    # FPS (simulation speed)
BG_COLOR = (255, 255, 255)  # White Background
NODE_RADIUS = 4
EDGE_WIDTH = 1

# Network Settings
TOTAL_PEOPLE=4000        # Total
AVERAGE_NEIGHBOURS=6     # Avg Connections
REWIRING_PROB=0.1        # Prob of Random Connection; Watts-Strogatz Parameter

# Disease Spread Settings
INITIAL_INFECTED_COUNT=10
DISEASE_SPREAD_PROB=0.3
INCUBATION_PERIOD=3
MIN_INFECTED_DURATION=7
MAX_INFECTED_DURATION=14

# Demographics
PROB_CHILD=0.2  
PROB_ADULT=0.5
PROB_OLD=0.3   

# Protection
VACCINE_COVERAGE=0.4   
VACCINE_EFFICIENCY=0.7   # Reduce infection chance by 70%
MASK_COVERAGE=0.3   
MASK_EFFICACY=0.5        # Reduce infection chance by 50%

# Probabilities of Death
DEATH_PROB_CHILD=0.001
DEATH_PROB_ADULT=0.01
DEATH_PROB_OLD=0.1

# States 
STATE_SUSCEPTIBLE=0
STATE_INCUBATING=1
STATE_INFECTED=2
STATE_RECOVERED=3
STATE_DEAD=4

# State Colors
COLOR_SUSCEPTIBLE = (0, 255, 0)     # Green
COLOR_INCUBATING = (255, 255, 0)    # Yellow
COLOR_INFECTED = (255, 50, 50)      # Red
COLOR_RECOVERED = (50, 100, 255)    # Blue
COLOR_DEAD = (50, 50, 50)           # Dark Grey/Black
COLOR_EDGE = (210, 210, 210)        # Light Grey lines



###### 2. GENERATE SOCIAL NETWORK ######

def create_social_network():
    # i) Create the Graph using Watts-Strogatz
    G= nx.watts_strogatz_graph(n=TOTAL_PEOPLE,k=AVERAGE_NEIGHBOURS,p=REWIRING_PROB)
    # ii) Force-Directed Layout (Spring Embedder)
    pos=nx.spring_layout(G,seed=42,k=0.15)
    print(f"Graph Created with {G.number_of_nodes()} nodes and {G.number_of_edges()} interactions.")
    return G,pos


# Convert Networkx Coords to Pygame Coords
def get_screen_coords(pos_dict):
    screen_coords = {}
    padding = 50 # Keep away from edges
    
    # Find bounding box for screen using max and min values for horizontal+vertical axes.
    xs = [x for x, y in pos_dict.values()]
    ys = [y for x, y in pos_dict.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    for node, (x, y) in pos_dict.items():
        # Normalize 0 to 1
        norm_x = (x - min_x) / (max_x - min_x)
        norm_y = (y - min_y) / (max_y - min_y)
        # Scale to Screen
        screen_x = int(padding + norm_x * (WIDTH - 2 * padding))
        screen_y = int(padding + norm_y * (HEIGHT - 2 * padding))
        screen_coords[node] = (screen_x, screen_y)
        
    return screen_coords


###### 3. INITIALIZATION OF POPULATION ######

def initialize_population(G):
    for i in G.nodes():
        # i. Assign Random Age
        rand_age=random.random()
        if rand_age < PROB_CHILD:
            age = 'child'
        elif rand_age < PROB_CHILD + PROB_ADULT:
            age = 'adult'
        else:
            age = 'old'

        # ii. Vaccine & Masks
        is_vaccinated=np.random.choice([True,False],p=[VACCINE_COVERAGE,1-VACCINE_COVERAGE])
        uses_mask=np.random.choice([True,False],p=[MASK_COVERAGE,1-MASK_COVERAGE])

        # iii. Initialize Attributes
        G.nodes[i]['state']=STATE_SUSCEPTIBLE
        G.nodes[i]['age']=age     
        G.nodes[i]['vaccinated']=is_vaccinated
        G.nodes[i]['mask']=uses_mask 
        G.nodes[i]['days_infected']=0
        G.nodes[i]['incubation_counter'] = 0

    # iv. Infect INITIAL_COUNT no.of people
    initial_infected=random.sample(list(G.nodes()),INITIAL_INFECTED_COUNT)
    for node in initial_infected:
        G.nodes[node]['state']=STATE_INFECTED


###### 4. SIMULATION LOGIC ######

def step_simulation(G):
    newly_infected=[]

    # STEP 1: TRANSMISSION

    infected_nodes = [n for n in G.nodes if G.nodes[n]['state'] == STATE_INFECTED]
    for node in infected_nodes:
        neighbors=G.neighbors(node)
        for neighbor in neighbors:
            if G.nodes[neighbor]['state']==STATE_SUSCEPTIBLE:

                # Base probability
                prob=DISEASE_SPREAD_PROB

                # Modify probability w.r.t vaccine & mask
                if G.nodes[neighbor]['vaccinated']:
                    prob=prob*(1-VACCINE_EFFICIENCY)
                if G.nodes[neighbor]['mask']:
                    prob=prob*(1-MASK_EFFICACY)

                # Bernoulli Distribution
                if random.random()<prob:
                    if neighbor not in newly_infected:
                        newly_infected.append(neighbor)

    # Make the newly infected incubate for 3 days.
    for node in newly_infected:
        G.nodes[node]['state']=STATE_INCUBATING

    # STEP 2: PROGRESSION

    for node in G.nodes():
        state=G.nodes[node]['state']

        # Incubation Over -> Infection
        if state==STATE_INCUBATING:
            G.nodes[node]['incubation_counter']+=1
            if G.nodes[node]['incubation_counter']>=INCUBATION_PERIOD:
                G.nodes[node]['state']=STATE_INFECTED

        # Infection -> Recovered/Dead
        elif state==STATE_INFECTED:
            G.nodes[node]['days_infected']+=1
            days=G.nodes[node]['days_infected']

            # Check for death after min duration
            if days>MIN_INFECTED_DURATION:
                age=G.nodes[node]['age']
                death_prob=0

                if age=='child': death_prob=DEATH_PROB_CHILD
                elif age=='adult':death_prob=DEATH_PROB_ADULT
                else:death_prob=DEATH_PROB_OLD

                # Random Prob for mortality
                if random.random()<death_prob:
                    G.nodes[node]['state']=STATE_DEAD
                    continue # If state=death then recovery impossible, so skip loop

            # Check for recovery after max duration
            if days>=MAX_INFECTED_DURATION:
                G.nodes[node]['state']=STATE_RECOVERED


###### 5. VISUALIZATION & RUN ######

def reset():
    G, raw_pos = create_social_network()
    initialize_population(G)
    screen_pos = get_screen_coords(raw_pos)
    return G, screen_pos

def show_final_bar_chart(counts):
    plt.figure(figsize=(6,4))
    plt.bar(
        ["Susceptible", "Incubating", "Infected", "Recovered", "Dead"],
        [
            counts[STATE_SUSCEPTIBLE],
            counts[STATE_INCUBATING],
            counts[STATE_INFECTED],
            counts[STATE_RECOVERED],
            counts[STATE_DEAD]
        ]
    )
    plt.ylabel("Population")
    plt.title("Final Disease Distribution")
    plt.tight_layout()
    plt.show()

def draw_color_legend_top_right(screen, font):
    padding = 10
    radius = 6
    line_gap = 20

    legend_items = [
        ("Susceptible", COLOR_SUSCEPTIBLE),
        ("Incubating", COLOR_INCUBATING),
        ("Infected", COLOR_INFECTED),
        ("Recovered", COLOR_RECOVERED),
        ("Dead", COLOR_DEAD)
    ]

    # Calculate box size
    box_width = 180
    box_height = line_gap * len(legend_items) + 20

    box_x = WIDTH - box_width - padding
    box_y = padding

    # Draw box
    pygame.draw.rect(screen, (245, 245, 245), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, (50, 50, 50), (box_x, box_y, box_width, box_height), 2)

    # Draw items
    for i, (label, color) in enumerate(legend_items):
        y = box_y + 15 + i * line_gap
        pygame.draw.circle(screen, color, (box_x + 15, y), radius)
        text = font.render(label, True, (0, 0, 0))
        screen.blit(text, (box_x + 30, y - 8))


def main():
    G, raw_pos = create_social_network()
    initialize_population(G)
    screen_pos = get_screen_coords(raw_pos)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SIR Network Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16, bold=True)
    big_font = pygame.font.SysFont("Arial", 30, bold=True)

    running = True
    day_count = 0
    paused = True 
    simulation_ended = False # Flag to track if virus is gone
    graph_shown=False

    while running:
        # 1. Input Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r: 
                    G, screen_pos = reset()
                    day_count = 0
                    paused = True
                    simulation_ended = False
                    graph_shown = False


        # 2. Count States
        counts = {0:0, 1:0, 2:0, 3:0, 4:0}
        for node in G.nodes():
            counts[G.nodes[node]['state']] += 1
        # Save history
        history["S"].append(counts[STATE_SUSCEPTIBLE])
        history["E"].append(counts[STATE_INCUBATING])
        history["I"].append(counts[STATE_INFECTED])
        history["R"].append(counts[STATE_RECOVERED])
        history["D"].append(counts[STATE_DEAD])
        

        # 3. Check for Simulation End
        # If no one is infected AND no one is incubating, the spread is over.
        if counts[STATE_INFECTED] == 0 and counts[STATE_INCUBATING] == 0:
            simulation_ended = True
        else:
            simulation_ended = False
        # Show final bar chart ONCE after outbreak ends
        if simulation_ended and not graph_shown:
           show_final_bar_chart(counts)
           graph_shown = True


        # 4. Run Logic (Only if not paused and not ended)
        if not paused and not simulation_ended:
            step_simulation(G)
            day_count += 1
        
        # 5. Drawing
        screen.fill(BG_COLOR)

       
        # Draw Edges 
        for u, v in G.edges(): 
            # pass
            start = screen_pos[u] 
            end = screen_pos[v] 
            pygame.draw.line(screen, COLOR_EDGE, start, end, EDGE_WIDTH)

        # Draw Nodes
        for node in G.nodes():
            state = G.nodes[node]['state']
            color = COLOR_SUSCEPTIBLE
            if state == STATE_INCUBATING: color = COLOR_INCUBATING
            elif state == STATE_INFECTED: color = COLOR_INFECTED
            elif state == STATE_RECOVERED: color = COLOR_RECOVERED
            elif state == STATE_DEAD: color = COLOR_DEAD
            
            pygame.draw.circle(screen, color, screen_pos[node], NODE_RADIUS)

        # Draw UI Box
        pygame.draw.rect(screen, (245, 245, 245), (5, 5, 200, 220)) # Light box
        pygame.draw.rect(screen, (50, 50, 50), (5, 5, 200, 220), 2) # Dark border

        # Dynamic Status Text
        status_text = "RUNNING"
        if paused: status_text = "PAUSED"
        if simulation_ended: status_text = "ENDED"

        stats_text = [
            f"STATUS: {status_text}",
            f"Time Step: {day_count}",
            "----------------",
            f"Healthy: {counts[STATE_SUSCEPTIBLE]}",
            f"Incubating: {counts[STATE_INCUBATING]}",
            f"Infected: {counts[STATE_INFECTED]}",
            f"Recovered: {counts[STATE_RECOVERED]}",
            f"Dead: {counts[STATE_DEAD]}",
            "----------------",
            "SPACE: Pause",
            "R: Restart"
        ]
        
        for i, line in enumerate(stats_text):
            # Change text color if simulation ended
            c = (200, 0, 0) if (simulation_ended and "STATUS" in line) else (0,0,0)
            text_surf = font.render(line, True, c)
            screen.blit(text_surf, (15, 15 + i * 18))
        
        draw_color_legend_top_right(screen, font)


            # Big Overlay if Ended
        if simulation_ended:
            msg = "OUTBREAK OVER"
            text_surf = big_font.render(msg, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=(WIDTH//2, 50))
            pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(20, 10))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10), 3)
            screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


# === HELPFUL FOR DEBUGGING  ===
# print("Step 1: Configuration Loaded.")
# print("Step 2: Generating Social Network.")
# print("Step 3: Initialize Population.")
# print("Step 4: Simulation Logic Defined.")
# print("Step 5: Visualized using Pygame.")

if __name__ == "__main__":
    main() 

