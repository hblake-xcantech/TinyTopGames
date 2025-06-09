#!/usr/bin/env python3
"""
Pong Game for Toddlers
=====================

A simple Pong game designed for toddlers with easy controls.

Usage:
  python game.py
"""

import pygame
import sys
from utils import check_screenshot

# Import game utilities for common functionality
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from game_utils import handle_common_events, quit_game, COLORS

# Config
WIDTH, HEIGHT = 1024, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SIZE = 20
FPS = 60

# Colors (using game_utils colors for consistency)
BLACK = COLORS['BLACK']
WHITE = COLORS['WHITE']
BLUE = COLORS['BLUE']

def run_game():
    """Main game function"""
    # Init pygame
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong Easy Mode")

    # Game objects
    paddle1_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    paddle2_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = 5
    ball_dy = 3
    score1 = 0
    score2 = 0

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        
        for event in pygame.event.get():
            # Handle common events (including ESC key)
            if not handle_common_events(event):
                running = False
                break
        
        # Simple AI and ball movement (placeholder logic)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and paddle1_y > 0:
            paddle1_y -= 5
        if keys[pygame.K_DOWN] and paddle1_y < HEIGHT - PADDLE_HEIGHT:
            paddle1_y += 5
        
        # Simple AI for paddle2
        if ball_y < paddle2_y + PADDLE_HEIGHT // 2:
            paddle2_y -= 3
        elif ball_y > paddle2_y + PADDLE_HEIGHT // 2:
            paddle2_y += 3
        
        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Rectangles for collision detection
        paddle1_rect = pygame.Rect(50, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        paddle2_rect = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball_rect = pygame.Rect(ball_x - BALL_SIZE // 2, ball_y - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

        # Bounce off paddles
        if ball_rect.colliderect(paddle1_rect) and ball_dx < 0:
            ball_dx = -ball_dx
            ball_x = paddle1_rect.right + BALL_SIZE // 2
        if ball_rect.colliderect(paddle2_rect) and ball_dx > 0:
            ball_dx = -ball_dx
            ball_x = paddle2_rect.left - BALL_SIZE // 2

        # Ball bouncing off top/bottom
        if ball_y - BALL_SIZE // 2 <= 0 or ball_y + BALL_SIZE // 2 >= HEIGHT:
            ball_dy = -ball_dy
        
        # Ball reset (simple scoring)
        if ball_x < 0:
            score2 += 1
            ball_x = WIDTH // 2
            ball_y = HEIGHT // 2
        elif ball_x > WIDTH:
            score1 += 1
            ball_x = WIDTH // 2
            ball_y = HEIGHT // 2

        # Draw everything
        screen.fill(BLACK)
        
        # Draw paddles
        pygame.draw.rect(screen, WHITE, (50, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - 50 - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        
        # Draw ball
        pygame.draw.rect(screen, WHITE, (ball_x - BALL_SIZE//2, ball_y - BALL_SIZE//2, BALL_SIZE, BALL_SIZE))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score1} - {score2}", True, BLUE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        check_screenshot(screen, os.path.join(os.path.dirname(__file__), "thumbnail.png"))
        clock.tick(FPS)

    # Use game_utils quit instead of pygame.quit() directly
    quit_game()

def main():
    """Main entry point"""
    run_game()

if __name__ == "__main__":
    main() 