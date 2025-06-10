#!/usr/bin/env python3
"""
Doodle Type Game for Tiny Top Games
===================================

A word guessing game where you type words to match doodle drawings.
Features random Google QuickDraw doodles with typing animations.

Usage:
  python game.py
"""

import pygame
import random
import sys
import os
import threading
import queue

try:
    from quickdraw import QuickDrawData
    QUICKDRAW_AVAILABLE = True
except ImportError:
    print("⚠️ QuickDraw not available - this game requires it to function")
    print("Please install with: pip install quickdraw")
    QUICKDRAW_AVAILABLE = False
    QuickDrawData = None

# Add path to access root-level modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils import screenshot_requested, check_screenshot
from game_utils import handle_common_events, quit_game, COLORS
from resources.ResourceManager import ResourceManager

WIDTH, HEIGHT = 1024, 600
BG = COLORS['WHITE']
TEXT = COLORS['BLACK']
GREEN = COLORS['GREEN']
FONT_SIZE = 48
WORDS = 5
FLASH_MS = 2000
DISPLAY_MS = 3000  # Display completed drawing for 3 seconds
PADDING = 20
CAP_PAD = 6
DOODLE_SIZE = 120
SMALL_W = 4
BIG_W = 6
SOUND_FILE = "pen_paper"
SOUND_LENGTH_MS = 33000  # 33 seconds

if QUICKDRAW_AVAILABLE:
    qd = QuickDrawData()
    CATEGORIES = qd.drawing_names
else:
    qd = None
    CATEGORIES = ["cat", "dog", "car", "house", "tree"]  # Fallback categories

# Async download system
download_queue = queue.Queue()
completed_downloads = {}
download_lock = threading.Lock()
download_thread = None

def download_worker():
    """Background thread worker for downloading doodles"""
    while True:
        try:
            word = download_queue.get(timeout=1)
            if word is None:  # Shutdown signal
                break
            
            print(f"Downloading {word} in background...")
            # Use more efficient download - only try 3 times instead of 100
            drawing = choose_efficient(word)
            
            with download_lock:
                completed_downloads[word] = drawing
            
            print(f"Completed download: {word}")
            download_queue.task_done()
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error downloading {word}: {e}")
            download_queue.task_done()

def choose_efficient(word, tries=3):
    """More efficient version that tries fewer times"""
    for _ in range(tries):
        try:
            d = qd.get_drawing(word)
            if d and d.recognized and sum(len(s) for s in d.strokes) > 20:
                return d
        except Exception as e:
            print(f"Network error for {word}: {e}")
            continue
    
    # Final attempt - return whatever we get
    try:
        return qd.get_drawing(word)
    except Exception as e:
        print(f"Failed to download {word}: {e}")
        return None

def choose(word, tries=100):
    for _ in range(tries):
        d = qd.get_drawing(word)
        if d and d.recognized and sum(len(s) for s in d.strokes) > 20:
            return d
    return qd.get_drawing(word)

def get_drawing_async(word):
    """Get a drawing, checking completed downloads first - NO SYNC FALLBACK"""
    with download_lock:
        if word in completed_downloads:
            return completed_downloads.pop(word)
    
    # Return None if not ready - don't block!
    return None

def is_drawing_ready(word):
    """Check if a drawing is ready without removing it"""
    with download_lock:
        return word in completed_downloads

def decode_stroke(stroke):
    """Convert stroke data to list of (x,y) coordinates."""
    # The quickdraw Python library returns strokes as [[x0, y0], [x1, y1], ...]
    # Each element is already an [x, y] coordinate pair
    if not stroke:
        return []
    
    # Convert list of [x, y] pairs to list of (x, y) tuples
    return [(pt[0], pt[1]) for pt in stroke if len(pt) >= 2]

def all_points(strokes):
    pts = []
    for s in strokes:
        pts.extend(decode_stroke(s))
    return pts

def get_bounds(strokes):
    """Get the bounding box for all strokes"""
    pts = all_points(strokes)
    if not pts:
        return 0, 0, 1, 1
    
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    
    w = maxx - minx
    h = maxy - miny
    
    # Handle edge cases
    if w == 0:
        w = 1
    if h == 0:
        h = 1
    
    return minx, miny, w, h

def render(strokes, size, color, width, progress=1.0):
    """Render strokes with animation progress"""
    if not strokes:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, size, size), width)
        return surf
    
    # Get bounds for ALL strokes (not just visible ones)
    minx, miny, w, h = get_bounds(strokes)
    
    # Calculate scale to fit in desired size
    scale = size / max(w, h)
    
    # Create surface with padding
    surf_w = int(w * scale) + width * 2
    surf_h = int(h * scale) + width * 2
    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    
    offset = width
    
    # Calculate how many points to draw based on progress
    total_points = sum(len(decode_stroke(s)) for s in strokes)
    points_to_draw = int(total_points * progress)
    
    points_drawn = 0
    
    # Draw strokes with animation
    for stroke in strokes:
        decoded = decode_stroke(stroke)
        if len(decoded) < 2:
            continue
        
        # Scale all points
        scaled = [((x - minx) * scale + offset, (y - miny) * scale + offset) for x, y in decoded]
        
        # Determine how many points of this stroke to draw
        stroke_points = len(decoded)
        
        if points_drawn + stroke_points <= points_to_draw:
            # Draw entire stroke
            pygame.draw.lines(surf, color, False, scaled, width)
            points_drawn += stroke_points
        elif points_drawn < points_to_draw:
            # Draw partial stroke
            points_in_stroke = points_to_draw - points_drawn
            if points_in_stroke >= 2:
                pygame.draw.lines(surf, color, False, scaled[:points_in_stroke], width)
            points_drawn = points_to_draw
            break
        else:
            # Don't draw this stroke yet
            break
    
    return surf

def render_word_with_progress(word, buf, font, color):
    """Render word with typed progress, showing underscores for spaces"""
    # Replace spaces with underscores for display
    display_word = word.replace(' ', '_')
    display_buf = buf.replace(' ', '_')
    
    ml = len(display_buf) if display_word.startswith(display_buf) else 0
    
    if ml > 0:
        # Render matched part in green
        matched = font.render(display_word[:ml], True, GREEN)
        unmatched = font.render(display_word[ml:], True, color)
        
        # Create combined surface
        total_width = matched.get_width() + unmatched.get_width()
        total_height = max(matched.get_height(), unmatched.get_height())
        combined = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        
        combined.blit(matched, (0, 0))
        combined.blit(unmatched, (matched.get_width(), 0))
        
        return combined, ml > 0
    else:
        return font.render(display_word, True, color), False

def build(word, font):
    d = get_drawing_async(word)
    if not d or not d.strokes:
        # Create placeholder if no drawing available
        surf = pygame.Surface((DOODLE_SIZE, DOODLE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, TEXT, (0, 0, DOODLE_SIZE, DOODLE_SIZE), 2)
    else:
        surf = render(d.strokes, DOODLE_SIZE, TEXT, SMALL_W)
    
    cap = font.render(word.replace(' ', '_'), True, TEXT)
    w = max(surf.get_width(), cap.get_width())
    h = surf.get_height() + CAP_PAD + cap.get_height()
    
    return dict(word=word, drawing=d, surface=surf, caption=cap, bounds=(w, h), pos=(0, 0))

def random_pos(bounds, rects):
    bw, bh = bounds
    for _ in range(300):
        x = random.randint(PADDING, WIDTH - bw - PADDING)
        y = random.randint(PADDING, HEIGHT - bh - PADDING)
        r = pygame.Rect(x, y, bw, bh)
        if all(not r.inflate(PADDING, PADDING).colliderect(o) for o in rects):
            return (x, y), r
    return (PADDING, PADDING), pygame.Rect(PADDING, PADDING, bw, bh)

def run_game():
    """Main game function"""
    if not QUICKDRAW_AVAILABLE:
        print("❌ Cannot run Doodle Type: QuickDraw library not available")
        print("This is likely due to Pillow installation issues on this system")
        print("Please try running other games in the collection!")
        return
        
    pygame.init()
    screenshot_mode = screenshot_requested()
    
    if not screenshot_mode:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Doodle Type")
    font = pygame.font.SysFont(None, FONT_SIZE)
    clock = pygame.time.Clock()
    
    # Initialize ResourceManager for sound
    resource_manager = None
    pen_sound_loaded = False
    if not screenshot_mode:
        try:
            resource_manager = ResourceManager()
            # Load pen sound as background music for special playback control
            pen_sound_path = resource_manager.get_sound_path(SOUND_FILE)
            if pen_sound_path:
                pygame.mixer.music.load(pen_sound_path)
                pen_sound_loaded = True
                print(f"Successfully loaded {SOUND_FILE} for background music")
            else:
                print(f"Warning: Could not find {SOUND_FILE}")
            print(f"ResourceManager initialized for sound")
        except Exception as e:
            print(f"Warning: Could not initialize ResourceManager: {e}")

    # Initialize game state
    items = []
    rects = []
    
    # Use fewer words in screenshot mode for faster loading
    word_count = 1 if screenshot_mode else WORDS
    selected_words = random.sample(CATEGORIES, word_count)
    
    # Start async download worker thread and begin downloads immediately
    if not screenshot_mode:
        download_thread = threading.Thread(target=download_worker, daemon=True)
        download_thread.start()
        
        # Start downloading the initial words immediately
        print(f"🎯 Starting background downloads for {len(selected_words)} words...")
        for word in selected_words:
            download_queue.put(word)
        
        # Also queue up some extra words for future use
        extra_words = random.sample([w for w in CATEGORIES if w not in selected_words], 
                                   min(10, len(CATEGORIES) - len(selected_words)))
        for word in extra_words:
            download_queue.put(word)
        print(f"🎯 Also queued {len(extra_words)} extra words for future use")
        
        # Preload voices for only the initial words
        if resource_manager:
            resource_manager.preload_voices(selected_words)
            print(f"🎤 Queued {len(selected_words)} voices for generation")
    
    # Handle screenshot mode - load one doodle and take screenshot
    if screenshot_mode:
        it = build(selected_words[0], font)
        it["pos"] = (WIDTH//2 - it["bounds"][0]//2, HEIGHT//2 - it["bounds"][1]//2)
        
        screen.fill(BG)
        x, y = it["pos"]
        
        # Center the drawing
        screen.blit(it["surface"], (x + (it["bounds"][0] - it["surface"].get_width()) // 2, y))
        
        # Draw caption
        display_cap = font.render(it["word"].replace(' ', '_'), True, TEXT)
        cap_x = x + (it["bounds"][0] - display_cap.get_width()) // 2
        cy = y + it["surface"].get_height() + CAP_PAD
        screen.blit(display_cap, (cap_x, cy))
        
        pygame.display.flip()
        check_screenshot(screen, os.path.join(os.path.dirname(__file__), "thumbnail.png"))
        return

    buf = ""
    flash = None
    running = True
    
    # Track which words we've already loaded
    loaded_words = set()
    
    while running:
        now = pygame.time.get_ticks()
        
        # Non-blocking check: add items as they become ready
        for word in selected_words:
            if word not in loaded_words and is_drawing_ready(word):
                print(f"✅ Adding ready doodle: {word}")
                
                it = build(word, font)
                if it["drawing"]:  # Only add if we got a valid drawing
                    it["pos"], r = random_pos(it["bounds"], rects)
                    items.append(it)
                    rects.append(r)
                    loaded_words.add(word)
                    
                    # Check if the current buffer matches the newly loaded word
                    if buf and it["word"] == buf:
                        draw_speed = random.uniform(0.8, 1.2)
                        flash = dict(start=now, item=it, idx=len(items)-1, draw_speed=draw_speed)
                        
                        # Play voice pronunciation
                        if resource_manager:
                            resource_manager.play_voice(it["word"])
                        
                        # Start playing pen sound
                        if pen_sound_loaded and it["drawing"] and it["drawing"].strokes:
                            actual_duration = (FLASH_MS / draw_speed) / 1000.0
                            max_start = max(0, (SOUND_LENGTH_MS / 1000.0) - actual_duration)
                            start_pos = random.uniform(0, max_start)
                            
                            print(f"Playing sound from position {start_pos:.2f}s for ~{actual_duration:.2f}s")
                            
                            pygame.mixer.music.set_volume(0.8)
                            pygame.mixer.music.play(0, start=start_pos)
                        
                        buf = ""
                        break
        
        for e in pygame.event.get():
            # Handle common events (including ESC key)
            if not handle_common_events(e):
                running = False
                break
                
            if e.type == pygame.KEYDOWN and not flash:
                if e.key == pygame.K_BACKSPACE:
                    buf = buf[:-1]
                elif e.key == pygame.K_SPACE:
                    # Check if adding space would match any word prefix
                    test_buf = buf + ' '
                    if any(it["word"].startswith(test_buf) for it in items):
                        buf += ' '
                    else:
                        # Invalid space - play error sound
                        if resource_manager:
                            try:
                                resource_manager.play_sound("error_008")
                            except Exception as e:
                                print(f"Could not play error sound: {e}")
                else:
                    c = e.unicode.lower()
                    if c.isalpha():
                        # Check if adding this character would match any word prefix
                        test_buf = buf + c
                        if any(it["word"].startswith(test_buf) for it in items):
                            buf += c
                            # Check if any word matches exactly
                            for idx, it in enumerate(items):
                                if it["word"] == buf:
                                    draw_speed = random.uniform(0.8, 1.2)
                                    flash = dict(start=now, item=it, idx=idx, draw_speed=draw_speed)
                                    
                                    # Play voice pronunciation
                                    if resource_manager:
                                        resource_manager.play_voice(it["word"])
                                    
                                    # Start playing pen sound at random position
                                    if pen_sound_loaded and it["drawing"] and it["drawing"].strokes:
                                        # Calculate actual drawing duration in seconds
                                        actual_duration = (FLASH_MS / draw_speed) / 1000.0
                                        # Choose random start position with enough time left
                                        max_start = max(0, (SOUND_LENGTH_MS / 1000.0) - actual_duration)
                                        start_pos = random.uniform(0, max_start)
                                        
                                        print(f"Playing sound from position {start_pos:.2f}s for ~{actual_duration:.2f}s")
                                        
                                        # Set volume first
                                        pygame.mixer.music.set_volume(0.8)
                                        # Play music from that position
                                        pygame.mixer.music.play(0, start=start_pos)
                                    
                                    buf = ""
                                    break
                        else:
                            # Invalid character - play error sound
                            if resource_manager:
                                try:
                                    resource_manager.play_sound("error_008")
                                    print(f"Invalid input '{c}' for current buffer '{buf}'")
                                except Exception as e:
                                    print(f"Could not play error sound: {e}")
        
        if flash:
            it = flash["item"]
            elapsed = now - flash["start"]
            # Apply randomized drawing speed
            drawing_prog = min(1, (elapsed * flash["draw_speed"]) / FLASH_MS)
            
            # Total time = drawing time + display time
            total_time = FLASH_MS / flash["draw_speed"] + DISPLAY_MS
            total_prog = elapsed / total_time
            
            if it["drawing"] and it["drawing"].strokes:
                # Render with animation progress (capped at 1.0 for drawing)
                big = render(it["drawing"].strokes, int(HEIGHT * 0.55), TEXT, BIG_W, progress=drawing_prog)
            else:
                big = pygame.Surface((int(HEIGHT * 0.55), int(HEIGHT * 0.55)), pygame.SRCALPHA)
                pygame.draw.rect(big, TEXT, big.get_rect(), BIG_W)
            
            screen.fill(BG)
            rect = big.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(big, rect)
            
            cap = font.render(it["word"].replace(' ', '_'), True, TEXT)
            screen.blit(cap, cap.get_rect(center=(WIDTH // 2, rect.bottom + CAP_PAD + cap.get_height() // 2)))
            
            pygame.display.flip()
            
            # Stop music when drawing completes (but keep displaying)
            if drawing_prog >= 1 and not flash.get("music_stopped", False):
                if pen_sound_loaded:
                    pygame.mixer.music.stop()
                    print("Stopped music")
                flash["music_stopped"] = True
            
            # End flash after both drawing and display phases complete
            if total_prog >= 1:
                # Try to find a ready replacement word
                available_words = []
                with download_lock:
                    available_words = list(completed_downloads.keys())
                
                if available_words:
                    new_word = random.choice(available_words)
                    print(f"🔄 Replacing with ready word: {new_word}")
                    new_it = build(new_word, font)
                    if new_it["drawing"]:
                        pos, r = random_pos(new_it["bounds"], [pygame.Rect(i["pos"], i["bounds"]) for i in items if i != it])
                        new_it["pos"] = pos
                        items[flash["idx"]] = new_it
                    else:
                        # If build failed, just remove the item
                        items.pop(flash["idx"])
                        rects.pop(flash["idx"])
                else:
                    # No replacement ready, just remove the completed item
                    print("⏳ No replacement ready, removing completed item")
                    items.pop(flash["idx"])
                    rects.pop(flash["idx"])
                
                # Queue up a new word for future use
                new_word_to_queue = random.choice(CATEGORIES)
                download_queue.put(new_word_to_queue)
                if resource_manager:
                    resource_manager.preload_voice(new_word_to_queue)
                
                flash = None
            
            clock.tick(60)
            continue

        screen.fill(BG)
        
        for it in items:
            x, y = it["pos"]
            
            # Center the drawing
            screen.blit(it["surface"], (x + (it["bounds"][0] - it["surface"].get_width()) // 2, y))
            
            # Draw caption with progress
            cx = x + (it["bounds"][0] - it["caption"].get_width()) // 2
            cy = y + it["surface"].get_height() + CAP_PAD
            
            # Check if current buffer matches this word
            matches = it["word"].startswith(buf)
            
            if matches and buf:
                # Render with highlighting
                rendered_cap, _ = render_word_with_progress(it["word"], buf, font, TEXT)
                # Center the rendered caption
                cap_x = x + (it["bounds"][0] - rendered_cap.get_width()) // 2
                screen.blit(rendered_cap, (cap_x, cy))
                # Draw green border
                pygame.draw.rect(screen, GREEN, pygame.Rect(it["pos"], it["bounds"]), 2)
            else:
                # Normal caption (with underscores for spaces)
                display_cap = font.render(it["word"].replace(' ', '_'), True, TEXT)
                cap_x = x + (it["bounds"][0] - display_cap.get_width()) // 2
                screen.blit(display_cap, (cap_x, cy))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Use game_utils quit instead of pygame.quit() directly
    quit_game()

def main():
    """Main entry point"""
    run_game()

if __name__ == "__main__":
    main() 