import pygame
from config import *

class Slider:
    def __init__(self, x, y, w, min_val, max_val, initial, label, is_int=False):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial
        self.is_int = is_int
        self.label = label
        self.dragging = False
        self.handle_rect = pygame.Rect(x, y - 5, 10, 30)
        self.update_handle()

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + int(ratio * self.rect.width)

    def draw(self, screen, font):
        val_str = f"{int(self.val)}" if self.is_int else f"{self.val:.2f}"
        txt = font.render(f"{self.label}: {val_str}", True, TEXT_COLOR)
        screen.blit(txt, (self.rect.x, self.rect.y - 25))
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        fill_w = self.handle_rect.centerx - self.rect.x
        pygame.draw.rect(screen, (100, 150, 200), (self.rect.x, self.rect.y, fill_w, 20))
        pygame.draw.rect(screen, (220, 220, 220), self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) or self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging and pygame.mouse.get_pressed()[0]:
            mouse_x = pygame.mouse.get_pos()[0]
            ratio = (mouse_x - self.rect.x) / self.rect.width
            ratio = max(0, min(1, ratio))
            self.val = self.min_val + ratio * (self.max_val - self.min_val)
            if self.is_int: self.val = int(round(self.val))
            self.update_handle()
            return True
        return False

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (60, 60, 60)
        self.color_active = (100, 150, 200)
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = None
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit():
                    self.text += event.unicode
        return None

    def draw(self, screen, font):
        self.txt_surface = font.render(self.text, True, (255, 255, 255))
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

def draw_sidebar_graph(screen, x, y, w, h, history, total_people):
    pygame.draw.rect(screen, (10, 10, 10), (x, y, w, h))
    pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), 1)
    
    if len(history['I']) < 2: return
    max_pop = max(total_people, 1) 
    data_len = len(history['I'])
    
    def plot_line(data_key, color):
        points = []
        for i, val in enumerate(history[data_key]):
            px = x + (i / max(1, data_len-1)) * w
            py = (y + h) - (val / max_pop) * h
            points.append((px, py))
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 2)

    plot_line("S", COLOR_SUSCEPTIBLE)
    plot_line("I", COLOR_INFECTIOUS)
    plot_line("R", COLOR_RECOVERED)
    plot_line("D", COLOR_DEAD)