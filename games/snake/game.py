#!/usr/bin/env python3
"""
Snake Game for Toddlers
=======================

A simple, forgiving Snake game designed for toddlers with:
- Single-step movement (arrow keys)
- Continuous movement when holding keys (500ms+ hold)
- No game over - just gentle collision blocking
- Happy sound effects
- Growing snake when eating food

Usage:
  python game.py
"""

import pygame
import sys
import os
import random
from utils import screenshot_requested, check_screenshot

# Import game utilities for common functionality
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from game_utils import handle_common_events, quit_game, COLORS

# Config
WIDTH, HEIGHT = 1024, 600
CELL_SIZE = 20
FPS = 10

# Colors (using game_utils colors for consistency)
BLACK = COLORS['BLACK']
GREEN = COLORS['GREEN']
RED = COLORS['RED']
BLUE = COLORS['BLUE']

def create_sound(frequency, duration, wave_type='sine'):
    """Create a sound effect with given frequency, duration and wave type"""
    try:
        import numpy as np
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames, False)
        
        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t) * 0.3
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t)) * 0.2
        else:  # triangle
            wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi * 0.3
            
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo_wave)
    except ImportError:
        # Fallback without numpy
        duration_ms = int(duration * 1000)
        sample_rate = 22050
        frames = int(duration_ms * sample_rate / 1000)
        sound_buffer = []
        cycle_length = sample_rate // frequency
        
        for i in range(frames):
            if wave_type == 'square':
                value = 8192 if (i // (cycle_length // 2)) % 2 else -8192
            else:  # sine approximation
                value = int(8192 * ((i % cycle_length) / cycle_length - 0.5) * 2)
            sound_buffer.extend([value, value])
        
        import struct
        sound_bytes = struct.pack('<%dh' % len(sound_buffer), *sound_buffer)
        return pygame.mixer.Sound(buffer=sound_bytes)

def setup_sounds():
    """Initialize all game sounds"""
    # Load sound or create different beep sounds
    sound_path = os.path.join(os.path.dirname(__file__), "brrrp.wav")
    if os.path.exists(sound_path):
        collision_sound = pygame.mixer.Sound(sound_path)
    else:
        collision_sound = create_sound(200, 0.3, 'square')  # Low, sad beep
    
    move_sound = create_sound(800, 0.05, 'sine')           # Quick tic
    eat_sound = create_sound(600, 0.2, 'triangle')         # Happy eating sound
    
    return collision_sound, move_sound, eat_sound

def spawn_food(snake):
    """Spawn food on the grid, avoiding snake positions and ensuring it's always visible"""
    # Calculate valid grid positions (ensure food is fully visible)
    max_grid_x = (WIDTH - CELL_SIZE) // CELL_SIZE
    max_grid_y = (HEIGHT - CELL_SIZE) // CELL_SIZE
    
    # Ensure we have at least some margin from edges
    min_x = 1
    min_y = 1
    max_x = max(min_x + 1, max_grid_x - 1)
    max_y = max(min_y + 1, max_grid_y - 1)
    
    attempts = 0
    while attempts < 100:  # Prevent infinite loop
        # Generate random grid position within safe bounds
        grid_x = random.randint(min_x, max_x)
        grid_y = random.randint(min_y, max_y)
        
        food_x = grid_x * CELL_SIZE
        food_y = grid_y * CELL_SIZE
        food_pos = (food_x, food_y)
        
        # Make sure food doesn't spawn on snake
        if food_pos not in snake:
            # Double-check that food is within visible area
            if (food_x >= 0 and food_x < WIDTH - CELL_SIZE and 
                food_y >= 0 and food_y < HEIGHT - CELL_SIZE):
                return food_pos
        
        attempts += 1
    
    # Fallback: place food at a safe default position
    safe_x = CELL_SIZE * 5
    safe_y = CELL_SIZE * 5
    return (safe_x, safe_y)

def move_snake(snake, food, direction_key, collision_sound, move_sound, eat_sound):
    """Helper function to move snake in given direction"""
    if direction_key == pygame.K_UP:
        new_head = (snake[0][0], snake[0][1] - CELL_SIZE)
    elif direction_key == pygame.K_DOWN:
        new_head = (snake[0][0], snake[0][1] + CELL_SIZE)
    elif direction_key == pygame.K_LEFT:
        new_head = (snake[0][0] - CELL_SIZE, snake[0][1])
    elif direction_key == pygame.K_RIGHT:
        new_head = (snake[0][0] + CELL_SIZE, snake[0][1])
    else:
        return False, food, 0
    
    # Check collision with walls - just block movement and play sound
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT):
        print("Brrrp! Wall hit - can't move there!")
        if collision_sound:
            collision_sound.play()
        return False, food, 0
    
    # Check collision with self - just block movement and play sound
    if new_head in snake:
        print("Brrrp! Can't move into yourself!")
        if collision_sound:
            collision_sound.play()
        return False, food, 0
    
    # Valid move - move snake
    snake.insert(0, new_head)
    
    # Check if food eaten
    if new_head == food:
        food = spawn_food(snake)
        print(f"Yum! Food eaten!")
        if eat_sound:
            eat_sound.play()
        # Snake grows automatically by not removing tail
        return True, food, 1
    else:
        snake.pop()  # Remove tail only if no food eaten
        if move_sound:
            move_sound.play()
        return True, food, 0

def run_game():
    """Main game function"""
    # Init pygame
    pygame.init()
    screenshot_mode = screenshot_requested()
    if not screenshot_mode:
        pygame.mixer.init()

    # Set up display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Easy Mode")

    # Initialize sounds (only if not in screenshot mode)
    if screenshot_mode:
        collision_sound = move_sound = eat_sound = None
    else:
        collision_sound, move_sound, eat_sound = setup_sounds()

    # Snake state - make sure snake starts on the grid
    start_x = (WIDTH // 2 // CELL_SIZE) * CELL_SIZE
    start_y = (HEIGHT // 2 // CELL_SIZE) * CELL_SIZE
    snake = [(start_x, start_y)]
    score = 0

    # Key holding state (only for normal mode)
    key_held = None
    key_hold_start = 0
    continuous_mode = False
    last_move_time = 0
    HOLD_THRESHOLD = 500  # ms to start continuous movement
    CONTINUOUS_MOVE_DELAY = 150  # ms between continuous moves

    # Food state
    food = spawn_food(snake)

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            # Handle common events (including ESC key)
            if not handle_common_events(event):
                running = False
                break
                
            if event.type == pygame.KEYDOWN:
                # Handle initial key press
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    # If this is a new key or we're not in continuous mode, move immediately
                    if key_held != event.key or not continuous_mode:
                        key_held = event.key
                        key_hold_start = current_time
                        continuous_mode = False
                        last_move_time = current_time
                        
                        # Perform the move
                        moved, food, score_gained = move_snake(snake, food, event.key, collision_sound, move_sound, eat_sound)
                        score += score_gained
                                
            elif event.type == pygame.KEYUP:
                # Stop continuous movement when key is released
                if event.key == key_held:
                    key_held = None
                    continuous_mode = False
        
        # Handle continuous movement when key is held
        if key_held and current_time - key_hold_start > HOLD_THRESHOLD:
            if not continuous_mode:
                continuous_mode = True
                print("Continuous mode activated!")
            
            # Move continuously at intervals
            if current_time - last_move_time > CONTINUOUS_MOVE_DELAY:
                last_move_time = current_time
                moved, food, score_gained = move_snake(snake, food, key_held, collision_sound, move_sound, eat_sound)
                score += score_gained

        # Draw everything
        screen.fill(BLACK)
        
        # Draw snake with white head
        for i, segment in enumerate(snake):
            if i == 0:  # Head
                pygame.draw.rect(screen, COLORS['WHITE'], (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
            else:  # Body
                pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        
        # Draw food
        pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLUE)
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