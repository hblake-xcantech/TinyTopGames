#!/usr/bin/env python3
"""
Pong Game for Toddlers
=====================

A simple Pong game designed for toddlers with easy controls.

Usage:
  python game.py           # Normal game mode
  python game.py --screenshot  # Generate thumbnail and exit
"""

import pygame
import sys
import argparse

# Config
WIDTH, HEIGHT = 1024, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SIZE = 20
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

def take_screenshot(screen):
    """Take a screenshot and save as thumbnail"""
    # Scale down to thumbnail size (320x240)
    thumbnail_surface = pygame.transform.scale(screen, (320, 240))
    
    # Save thumbnail
    import os
    thumbnail_path = os.path.join(os.path.dirname(__file__), "thumbnail.png")
    pygame.image.save(thumbnail_surface, thumbnail_path)
    print(f"Thumbnail saved to {thumbnail_path}")

def run_game(screenshot_mode=False):
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
        # In screenshot mode, just draw one frame and exit
        if screenshot_mode:
            # Draw everything
            screen.fill(BLACK)
            
            # Draw paddles
            pygame.draw.rect(screen, WHITE, (50, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.rect(screen, WHITE, (WIDTH - 50 - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
            
            # Draw ball
            pygame.draw.rect(screen, WHITE, (ball_x - BALL_SIZE//2, ball_y - BALL_SIZE//2, BALL_SIZE, BALL_SIZE))
            
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Pong Game - {score1} : {score2}", True, BLUE)
            screen.blit(score_text, (10, 10))
            
            pygame.display.flip()
            take_screenshot(screen)
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
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
        
        # Ball bouncing
        if ball_y <= 0 or ball_y >= HEIGHT:
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
        clock.tick(FPS)

    pygame.quit()

def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(description='Pong Game for Toddlers')
    parser.add_argument('--screenshot', action='store_true', 
                       help='Generate thumbnail screenshot and exit')
    
    args = parser.parse_args()
    
    if args.screenshot:
        print("Generating thumbnail...")
        run_game(screenshot_mode=True)
        print("Thumbnail generation complete!")
    else:
        run_game(screenshot_mode=False)

if __name__ == "__main__":
    main() 