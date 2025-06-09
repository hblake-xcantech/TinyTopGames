#!/usr/bin/env python3
"""
Game Utilities for Tiny Top Games
=================================

Common utilities that all games can use to ensure consistent behavior
across the game collection.

Features:
- ESC key handling to return to main menu with sound
- Common color definitions
- Utility functions for game development
"""

import pygame
import sys
import os
import time

# Try to import ResourceManager for sounds
try:
    from resources.ResourceManager import ResourceManager
    _resource_manager = None
    
    def get_resource_manager():
        global _resource_manager
        if _resource_manager is None:
            try:
                _resource_manager = ResourceManager()
            except Exception as e:
                print(f"Warning: Could not initialize ResourceManager: {e}")
                _resource_manager = False  # Mark as failed to avoid retrying
        return _resource_manager if _resource_manager is not False else None
        
except ImportError:
    def get_resource_manager():
        return None

# Common colors that games can use
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'ORANGE': (255, 165, 0),
    'PINK': (255, 192, 203),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (200, 200, 200),
    'DARK_GRAY': (64, 64, 64)
}

def play_exit_sound_and_wait():
    """Play the exit sound and wait for it to finish"""
    resources = get_resource_manager()
    if resources:
        resources.play_sound("minimize_006")
        # Wait a bit for the sound to finish playing
        # minimize_006 is typically around 0.5-1 second, so wait 1.2 seconds to be safe
        time.sleep(1.2)

def handle_common_events(event):
    """
    Handle common events that all games should respond to.
    Call this function in your game's event loop.
    
    Returns:
        bool: True if the game should continue, False if it should exit
    """
    if event.type == pygame.QUIT:
        # Play exit sound and wait for it to complete
        play_exit_sound_and_wait()
        return False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            # ESC key pressed - play exit sound and wait for it to complete
            play_exit_sound_and_wait()
            return False
    
    return True

def setup_game_window(width, height, title):
    """
    Set up a standard game window with consistent settings.
    
    Args:
        width (int): Window width
        height (int): Window height  
        title (str): Window title
        
    Returns:
        tuple: (screen, clock) - Pygame screen surface and clock object
    """
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    
    return screen, clock

def draw_text_centered(surface, text, font, color, y_position):
    """
    Draw text centered horizontally on the surface.
    
    Args:
        surface: Pygame surface to draw on
        text (str): Text to draw
        font: Pygame font object
        color: Text color tuple (r, g, b)
        y_position (int): Y position for the text
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(surface.get_width() // 2, y_position))
    surface.blit(text_surface, text_rect)

def create_basic_font(size=36):
    """
    Create a basic font for games to use.
    
    Args:
        size (int): Font size
        
    Returns:
        pygame.font.Font: Font object
    """
    return pygame.font.Font(None, size)

def quit_game():
    """
    Properly quit the game and return to main menu.
    """
    pygame.quit()
    # Don't call sys.exit() - just let the function return so main_menu can continue 