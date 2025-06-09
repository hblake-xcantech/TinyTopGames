import pygame
import sys
import os
import random

# Config
WIDTH, HEIGHT = 1024, 600
CELL_SIZE = 20
FPS = 10

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Init pygame
pygame.init()
pygame.mixer.init()

# Load sound or create different beep sounds
sound_path = os.path.join(os.path.dirname(__file__), "brrrp.wav")
if os.path.exists(sound_path):
    collision_sound = pygame.mixer.Sound(sound_path)
else:
    collision_sound = None

# Create different sound effects
def create_sound(frequency, duration, wave_type='sine'):
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

# Create sound effects
if not collision_sound:
    collision_sound = create_sound(200, 0.3, 'square')  # Low, sad beep
move_sound = create_sound(800, 0.05, 'sine')           # Quick tic
eat_sound = create_sound(600, 0.2, 'triangle')         # Happy eating sound

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tiny Top Games - Snake Easy Mode")

# Snake state
# Make sure snake starts on the grid by rounding to nearest grid position
start_x = (WIDTH // 2 // CELL_SIZE) * CELL_SIZE
start_y = (HEIGHT // 2 // CELL_SIZE) * CELL_SIZE
snake = [(start_x, start_y)]
score = 0

# Key holding state
key_held = None
key_hold_start = 0
continuous_mode = False
last_move_time = 0
HOLD_THRESHOLD = 500  # ms to start continuous movement
CONTINUOUS_MOVE_DELAY = 150  # ms between continuous moves

# Food state
def spawn_food():
    while True:
        # Make sure food is perfectly aligned with the grid by using the same logic as snake movement
        food_x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        food_y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        food_pos = (food_x, food_y)
        if food_pos not in snake:
            return food_pos

food = spawn_food()

# Game loop
clock = pygame.time.Clock()
running = True

def move_snake(direction_key):
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
        return False
    
    # Check collision with walls - just block movement and play sound
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT):
        print("Brrrp! Wall hit - can't move there!")
        collision_sound.play()
        return False
    
    # Check collision with self - just block movement and play sound
    if new_head in snake:
        print("Brrrp! Can't move into yourself!")
        collision_sound.play()
        return False
    
    # Valid move - move snake
    snake.insert(0, new_head)
    
    # Check if food eaten
    if new_head == food:
        global score, food
        score += 1
        food = spawn_food()
        print(f"Yum! Score: {score}")
        eat_sound.play()  # Play happy eating sound
        # Snake grows automatically by not removing tail
    else:
        snake.pop()  # Remove tail only if no food eaten
        move_sound.play()  # Play tic sound for normal movement
    
    return True

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Handle initial key press
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                # If this is a new key or we're not in continuous mode, move immediately
                if key_held != event.key or not continuous_mode:
                    key_held = event.key
                    key_hold_start = current_time
                    continuous_mode = False
                    last_move_time = current_time
                    
                    # Perform the move
                    move_snake(event.key)
                            
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
            move_snake(key_held)

    # Draw everything
    screen.fill(BLACK)
    
    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
    
    # Draw food
    pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))
    
    # Draw score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLUE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
