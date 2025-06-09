#!/usr/bin/env python3
"""
Tiny Top Games - Kid-Friendly Main Menu
=======================================

A bright, colorful, and fun game launcher designed specifically for toddlers
and young children. Features large thumbnails, friendly fonts, smooth animations,
and a cheerful interface that makes game selection exciting and easy.

Controls:
- LEFT/RIGHT arrows: Navigate games
- ENTER: Play selected game
- ESC: Exit

Design Features:
- Bright gradient background
- Large, centered game preview
- Smooth scaling animations
- Kid-friendly fonts and colors
- Clear, simple instructions
- No intimidating programmer-style elements

Game Discovery:
- Automatically finds games in games/ directory
- Shows game thumbnails and names
- Scales thumbnails for optimal viewing
"""

import pygame
import sys
import os
import subprocess
import math
from pathlib import Path
from resources.ResourceManager import ResourceManager

# Kid-Friendly Config
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 600
THUMBNAIL_SIZE = (280, 210)  # Larger thumbnails for better visibility
PREVIEW_SIZE = (350, 260)    # Main preview size (slightly smaller to fit better)

# Cheerful Colors
SKY_BLUE = (135, 206, 250)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
BRIGHT_GREEN = (50, 205, 50)
SUNNY_YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
PURPLE = (147, 112, 219)
DARK_BLUE = (25, 25, 112)
SHADOW_GRAY = (0, 0, 0, 50)  # Semi-transparent for shadows

# Animation settings
SCALE_SPEED = 0.1
BOUNCE_AMOUNT = 0.05  # Reduced bounce for less distraction

class GameInfo:
    """Container for game information with animation properties"""
    def __init__(self, name, path, description="", thumbnail=None):
        self.name = name
        self.path = path
        self.description = description
        self.thumbnail = thumbnail
        self.display_name = self.name.replace('_', ' ').title()
        
        # Animation properties
        self.scale = 1.0
        self.target_scale = 1.0
        self.bounce_offset = 0
        self.bounce_speed = 0

def create_gradient_background(width, height):
    """Create a beautiful sky gradient background"""
    background = pygame.Surface((width, height))
    
    # Create vertical gradient from sky blue to light blue
    for y in range(height):
        # Calculate color blend ratio
        ratio = y / height
        r = int(SKY_BLUE[0] * (1 - ratio) + LIGHT_BLUE[0] * ratio)
        g = int(SKY_BLUE[1] * (1 - ratio) + LIGHT_BLUE[1] * ratio)
        b = int(SKY_BLUE[2] * (1 - ratio) + LIGHT_BLUE[2] * ratio)
        
        pygame.draw.line(background, (r, g, b), (0, y), (width, y))
    
    return background

def draw_rounded_rect(surface, color, rect, corner_radius):
    """Draw a rounded rectangle (simplified version)"""
    # Draw main rectangle
    pygame.draw.rect(surface, color, rect)
    
    # Draw corner circles to create rounded effect
    x, y, w, h = rect
    pygame.draw.circle(surface, color, (x + corner_radius, y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + w - corner_radius, y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + corner_radius, y + h - corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + w - corner_radius, y + h - corner_radius), corner_radius)

def draw_shadow(surface, rect, offset=5):
    """Draw a soft shadow behind a rectangle"""
    shadow_surf = pygame.Surface((rect.width + offset * 2, rect.height + offset * 2), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
    draw_rounded_rect(shadow_surf, SHADOW_GRAY, shadow_rect, 10)
    
    # Blur effect (simplified)
    for i in range(3):
        temp_surf = pygame.transform.smoothscale(shadow_surf, 
                                                (shadow_surf.get_width() - 2, 
                                                 shadow_surf.get_height() - 2))
        shadow_surf = pygame.transform.smoothscale(temp_surf, 
                                                  (shadow_surf.get_width(), 
                                                   shadow_surf.get_height()))
    
    surface.blit(shadow_surf, (rect.x - offset, rect.y - offset))

def create_fun_thumbnail(size, game_name):
    """Create a colorful placeholder thumbnail with game name"""
    surface = pygame.Surface(size)
    
    # Bright colorful background based on game name
    colors = [BRIGHT_GREEN, SUNNY_YELLOW, ORANGE, PINK, PURPLE]
    color_index = hash(game_name) % len(colors)
    background_color = colors[color_index]
    
    surface.fill(background_color)
    
    # Add fun shapes
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Draw fun geometric shapes
    pygame.draw.circle(surface, WHITE, (center_x, center_y), 40, 5)
    pygame.draw.rect(surface, WHITE, (center_x - 30, center_y - 30, 60, 60), 5)
    
    # Add game name
    font = pygame.font.Font(None, 24)
    text = font.render(game_name.upper(), True, DARK_BLUE)
    text_rect = text.get_rect(center=(center_x, center_y + 60))
    surface.blit(text, text_rect)
    
    return surface

def discover_games():
    """Discover all games in the games/ directory"""
    games = []
    games_dir = Path("games")
    
    if not games_dir.exists():
        print("Warning: games/ directory not found!")
        return games
    
    for game_dir in games_dir.iterdir():
        if not game_dir.is_dir():
            continue
            
        game_py = game_dir / "game.py"
        if not game_py.exists():
            continue
        
        # Load description
        description_file = game_dir / "description.txt"
        description = ""
        if description_file.exists():
            try:
                description = description_file.read_text().strip()
            except Exception:
                pass
        
        # Load thumbnail
        thumbnail_file = game_dir / "thumbnail.png"
        thumbnail = None
        if thumbnail_file.exists():
            try:
                thumbnail = pygame.image.load(str(thumbnail_file))
                thumbnail = pygame.transform.scale(thumbnail, THUMBNAIL_SIZE)
            except Exception:
                pass
        
        # Create fun placeholder if no thumbnail
        if thumbnail is None:
            thumbnail = create_fun_thumbnail(THUMBNAIL_SIZE, game_dir.name)
        
        games.append(GameInfo(
            name=game_dir.name,
            path=str(game_py),
            description=description,
            thumbnail=thumbnail
        ))
    
    return sorted(games, key=lambda g: g.name)

def launch_game(game_path):
    """Launch a game and wait for it to complete"""
    try:
        print(f"Starting {game_path}...")
        subprocess.run([sys.executable, game_path], cwd=os.getcwd())
        return True
    except Exception as e:
        print(f"Error launching game: {e}")
        return False

def main():
    """Main kid-friendly menu loop"""
    # Initialize Pygame
    pygame.init()
    
    # Initialize ResourceManager for sounds
    try:
        resources = ResourceManager()
    except Exception as e:
        print(f"Warning: Could not initialize ResourceManager: {e}")
        resources = None
    
    # Set up display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tiny Top Games")
    clock = pygame.time.Clock()
    
    # Create background
    background = create_gradient_background(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Load fun fonts (adjusted sizes for better layout)
    title_font = pygame.font.Font(None, 56)      # Smaller title
    game_name_font = pygame.font.Font(None, 42)  # Game names
    instruction_font = pygame.font.Font(None, 32) # Instructions
    small_font = pygame.font.Font(None, 24)      # Small text
    
    # Discover games
    games = discover_games()
    
    if not games:
        # Show "no games" message with friendly graphics
        no_games_font = pygame.font.Font(None, 48)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if resources:
                        resources.play_sound("minimize_006")
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if resources:
                            resources.play_sound("minimize_006")
                        pygame.quit()
                        return
            
            screen.blit(background, (0, 0))
            
            # Friendly "no games" message
            title_text = title_font.render("Tiny Top Games", True, DARK_BLUE)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
            screen.blit(title_text, title_rect)
            
            msg_text = no_games_font.render("No games found!", True, DARK_BLUE)
            msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, 300))
            screen.blit(msg_text, msg_rect)
            
            help_text = instruction_font.render("Add games to the games/ folder!", True, DARK_BLUE)
            help_rect = help_text.get_rect(center=(WINDOW_WIDTH // 2, 350))
            screen.blit(help_text, help_rect)
            
            pygame.display.flip()
            clock.tick(60)
    
    # Menu state
    selected_index = 0
    
    # Animation timing
    bounce_timer = 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        bounce_timer += dt * 2  # Bounce speed (reduced)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if resources:
                    resources.play_sound("minimize_006")
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if resources:
                        resources.play_sound("minimize_006")
                    running = False
                elif event.key == pygame.K_LEFT:
                    if resources:
                        resources.play_sound("click_001")
                    selected_index = (selected_index - 1) % len(games)
                elif event.key == pygame.K_RIGHT:
                    if resources:
                        resources.play_sound("click_001")
                    selected_index = (selected_index + 1) % len(games)
                elif event.key == pygame.K_RETURN and games:
                    # Launch selected game with confirmation sound
                    if resources:
                        resources.play_sound("confirmation_001")
                    selected_game = games[selected_index]
                    launch_game(selected_game.path)
                    # Reinitialize display after game
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    pygame.display.set_caption("Tiny Top Games")
        
        # Update animations
        for i, game in enumerate(games):
            # Set target scale based on selection
            if i == selected_index:
                game.target_scale = 1.0 + math.sin(bounce_timer) * BOUNCE_AMOUNT
            else:
                game.target_scale = 0.8
            
            # Smooth scale transition
            game.scale += (game.target_scale - game.scale) * SCALE_SPEED
        
        # Draw everything
        screen.blit(background, (0, 0))
        
        # Draw title with fun styling (positioned higher and smaller)
        title_text = title_font.render("Tiny Top Games", True, DARK_BLUE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
        screen.blit(title_text, title_rect)
        
        if games:
            selected_game = games[selected_index]
            
            # Draw main game preview (large, centered, positioned better)
            preview_size = (int(PREVIEW_SIZE[0] * selected_game.scale), 
                           int(PREVIEW_SIZE[1] * selected_game.scale))
            preview_thumbnail = pygame.transform.scale(selected_game.thumbnail, preview_size)
            preview_rect = preview_thumbnail.get_rect(center=(WINDOW_WIDTH // 2, 200))
            
            # Draw shadow behind preview
            shadow_rect = pygame.Rect(preview_rect.x - 5, preview_rect.y - 5, 
                                    preview_rect.width + 10, preview_rect.height + 10)
            draw_shadow(screen, shadow_rect)
            
            # Draw white background with rounded corners
            bg_rect = pygame.Rect(preview_rect.x - 10, preview_rect.y - 10,
                                preview_rect.width + 20, preview_rect.height + 20)
            draw_rounded_rect(screen, WHITE, bg_rect, 15)
            
            # Draw the game thumbnail
            screen.blit(preview_thumbnail, preview_rect)
            
            # Draw game name (positioned below preview)
            name_text = game_name_font.render(selected_game.display_name, True, DARK_BLUE)
            name_rect = name_text.get_rect(center=(WINDOW_WIDTH // 2, 350))
            screen.blit(name_text, name_rect)
            
            # Draw fun "Press ENTER to Play!" instruction
            play_text = instruction_font.render("Press ENTER to Play!", True, BRIGHT_GREEN)
            play_rect = play_text.get_rect(center=(WINDOW_WIDTH // 2, 385))
            screen.blit(play_text, play_rect)
            
            # Draw navigation hints (only if multiple games)
            if len(games) > 1:
                nav_text = instruction_font.render("LEFT/RIGHT - Choose Game", True, ORANGE)
                nav_rect = nav_text.get_rect(center=(WINDOW_WIDTH // 2, 420))
                screen.blit(nav_text, nav_rect)
            
            # Draw small thumbnails of other games at the bottom (only if multiple games)
            if len(games) > 1:
                side_size = (60, 45)  # Smaller side thumbnails
                y_pos = 460
                spacing = 80
                
                # Only show up to 6 other games to avoid crowding
                other_games = [g for i, g in enumerate(games) if i != selected_index]
                visible_other_games = other_games[:6]
                
                # Calculate starting position to center the row
                total_width = len(visible_other_games) * spacing
                start_x = (WINDOW_WIDTH - total_width) // 2 + spacing // 2
                
                for i, game in enumerate(visible_other_games):
                    x_pos = start_x + i * spacing
                    
                    small_thumb = pygame.transform.scale(game.thumbnail, side_size)
                    thumb_rect = small_thumb.get_rect(center=(x_pos, y_pos))
                    
                    # Draw small background
                    bg_rect = pygame.Rect(thumb_rect.x - 3, thumb_rect.y - 3,
                                        thumb_rect.width + 6, thumb_rect.height + 6)
                    draw_rounded_rect(screen, WHITE, bg_rect, 5)
                    
                    screen.blit(small_thumb, thumb_rect)
            
            # Show game count if multiple games
            if len(games) > 1:
                count_text = small_font.render(f"Game {selected_index + 1} of {len(games)}", True, DARK_BLUE)
                count_rect = count_text.get_rect(center=(WINDOW_WIDTH // 2, 520))
                screen.blit(count_text, count_rect)
        
        # Draw exit instruction
        exit_text = small_font.render("Press ESC to exit", True, DARK_BLUE)
        screen.blit(exit_text, (10, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    pygame.quit()
    print("Thanks for playing!")

if __name__ == "__main__":
    main() 