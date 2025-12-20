import pygame, sys
import matplotlib.pyplot as plt
from config import *
from ui import Slider, InputBox, draw_sidebar_graph
from logic import create_social_network, get_screen_coords, initialize_population, step_simulation

# matplot bar chart
def show_final_bar_chart(counts):
    plt.figure(figsize=(6,4))
    plt.bar(
        ["Susceptible", "Incubating", "Infected", "Recovered", "Dead"],
        [counts[STATE_SUSCEPTIBLE], counts[STATE_INCUBATING], counts[STATE_INFECTED], counts[STATE_RECOVERED], counts[STATE_DEAD]]
    )
    plt.ylabel("Population")
    plt.title("Final Disease Distribution")
    plt.tight_layout()
    plt.show()

def main():
    # Initial Simulation State
    TOTAL_PEOPLE = 400
    DISEASE_SPREAD_PROB = 0.4
    INITIAL_INFECTED_COUNT = 10
    MAX_INFECTED_DURATION = 14
    INCUBATION_PERIOD = 3
    MIN_INFECTED_DURATION = 7
    
    show_edges_flag = False
    history = {"S": [], "E": [], "I": [], "R": [], "D": []}

    # Setup Logic
    G, raw_pos = create_social_network(TOTAL_PEOPLE, 4, 0.1)
    initialize_population(G, INITIAL_INFECTED_COUNT)
    screen_pos = get_screen_coords(raw_pos)

    # Setup Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SEIR Simulation - Final Project")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 14)
    title_font = pygame.font.SysFont("Arial", 20, bold=True)

    # Setup UI
    input_pop = InputBox(20, 310, 140, 30, text=str(TOTAL_PEOPLE))
    slider_prob = Slider(20, 370, 260, 0.0, 1.0, DISEASE_SPREAD_PROB, "Infection Probability")
    slider_init = Slider(20, 440, 260, 1, 50, INITIAL_INFECTED_COUNT, "Initial Infected", is_int=True)
    slider_dur  = Slider(20, 510, 260, 5, 30, MAX_INFECTED_DURATION, "Recovery Period (days)", is_int=True)

    btn_edges_rect = pygame.Rect(20, 560, 120, 30)
    btn_pause_rect = pygame.Rect(20, 650, 120, 40)
    btn_reset_rect = pygame.Rect(160, 650, 120, 40)

    running = True
    paused = True 
    simulation_ended = False
    graph_shown = False
    day_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

            # Inputs & Sliders
            new_pop_str = input_pop.handle_event(event)
            if new_pop_str and new_pop_str.isdigit() and int(new_pop_str) > 0:
                TOTAL_PEOPLE = int(new_pop_str)
                # Reset Trigger
                paused, simulation_ended, graph_shown, day_count = True, False, False, 0
                history = {"S": [], "E": [], "I": [], "R": [], "D": []}
                G, raw_pos = create_social_network(TOTAL_PEOPLE, 4, 0.1)
                initialize_population(G, INITIAL_INFECTED_COUNT)
                screen_pos = get_screen_coords(raw_pos)

            slider_prob.handle_event(event)
            slider_init.handle_event(event)
            slider_dur.handle_event(event)

            # Buttons
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_edges_rect.collidepoint(event.pos): show_edges_flag = not show_edges_flag
                if btn_pause_rect.collidepoint(event.pos): paused = not paused
                if btn_reset_rect.collidepoint(event.pos):
                    paused, simulation_ended, graph_shown, day_count = True, False, False, 0
                    history = {"S": [], "E": [], "I": [], "R": [], "D": []}
                    G, raw_pos = create_social_network(TOTAL_PEOPLE, 4, 0.1)
                    initialize_population(G, int(slider_init.val))
                    screen_pos = get_screen_coords(raw_pos)

        # Update Variables from Sliders
        DISEASE_SPREAD_PROB = slider_prob.val
        INITIAL_INFECTED_COUNT = int(slider_init.val)
        MAX_INFECTED_DURATION = int(slider_dur.val)

        # Count States
        counts = {0:0, 1:0, 2:0, 3:0, 4:0}
        for node in G.nodes(): counts[G.nodes[node]['state']] += 1

        # Logic Step
        if not paused and not simulation_ended:
            if counts[STATE_INFECTED] > 0 or counts[STATE_INCUBATING] > 0:
                step_simulation(G, DISEASE_SPREAD_PROB, INCUBATION_PERIOD, MIN_INFECTED_DURATION, MAX_INFECTED_DURATION)
                day_count += 1
                history["S"].append(counts[STATE_SUSCEPTIBLE])
                history["E"].append(counts[STATE_INCUBATING])
                history["I"].append(counts[STATE_INFECTED])
                history["R"].append(counts[STATE_RECOVERED])
                history["D"].append(counts[STATE_DEAD])
            else:
                simulation_ended = True

        if simulation_ended and not graph_shown:
            show_final_bar_chart(counts)
            graph_shown = True

        # Drawing
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, SIDEBAR_COLOR, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        
        # Sidebar
        screen.blit(font.render("S / E / I / R over time", True, TEXT_COLOR), (20, 25))
        draw_sidebar_graph(screen, 20, 50, 280, 210, history, TOTAL_PEOPLE)
        
        screen.blit(font.render("Total Population (Type & Enter):", True, TEXT_COLOR), (20, 285))
        input_pop.draw(screen, font)
        
        slider_prob.draw(screen, font)
        slider_init.draw(screen, font)
        slider_dur.draw(screen, font)

        # Buttons
        col = (100, 100, 100) if not show_edges_flag else (50, 150, 50)
        pygame.draw.rect(screen, col, btn_edges_rect)
        screen.blit(font.render("Show Edges", True, (255,255,255)), (btn_edges_rect.x + 20, btn_edges_rect.y + 7))

        pygame.draw.rect(screen, (80, 80, 80), btn_pause_rect)
        p_text = "Resume" if paused else "Pause"
        screen.blit(font.render(p_text, True, (255,255,255)), (btn_pause_rect.centerx - 20, btn_pause_rect.centery - 8))

        pygame.draw.rect(screen, (80, 80, 80), btn_reset_rect)
        screen.blit(font.render("Reset", True, (255,255,255)), (btn_reset_rect.centerx - 15, btn_reset_rect.centery - 8))

        # Main View
        screen.blit(title_font.render("Simulation of Infectious Disease Spread", True, TEXT_COLOR), (SIDEBAR_WIDTH + 20, 20))
        screen.blit(font.render(f"Day: {day_count}   |   Total: {TOTAL_PEOPLE}", True, (150, 150, 150)), (SIDEBAR_WIDTH + 20, 50))

        if show_edges_flag:
            for u, v in G.edges():
                pygame.draw.line(screen, COLOR_EDGE, screen_pos[u], screen_pos[v], EDGE_WIDTH)

        for node in G.nodes():
            state = G.nodes[node]['state']
            color = COLOR_SUSCEPTIBLE
            if state == STATE_INCUBATING: color = COLOR_INCUBATING
            elif state == STATE_INFECTED: color = COLOR_INFECTED
            elif state == STATE_RECOVERED: color = COLOR_RECOVERED
            elif state == STATE_DEAD: color = COLOR_DEAD
            pygame.draw.circle(screen, color, screen_pos[node], NODE_RADIUS)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()