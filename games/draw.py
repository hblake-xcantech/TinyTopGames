import pygame, random, sys
from quickdraw import QuickDrawData

WIDTH, HEIGHT = 800, 600
BG = (255,255,255)
TEXT = (0,0,0)
GREEN = (0,150,0)
FONT_SIZE=48
WORDS=5
FLASH_MS=2000
PADDING=20
CAP_PAD=6
DOODLE_SIZE=120
SMALL_W=4
BIG_W=6
SOUND_FILE = "pen_paper.wav"
SOUND_LENGTH_MS = 33000  # 33 seconds

qd=QuickDrawData()
CATEGORIES=qd.drawing_names

def choose(word, tries=100):
    for _ in range(tries):
        d=qd.get_drawing(word)
        if d and d.recognized and sum(len(s) for s in d.strokes)>20:
            return d
    return qd.get_drawing(word)

def decode_stroke(stroke):
    """Convert stroke data to list of (x,y) coordinates."""
    # The quickdraw Python library returns strokes as [[x0, y0], [x1, y1], ...]
    # Each element is already an [x, y] coordinate pair
    if not stroke:
        return []
    
    # Convert list of [x, y] pairs to list of (x, y) tuples
    return [(pt[0], pt[1]) for pt in stroke if len(pt) >= 2]

def all_points(strokes):
    pts=[]
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
    d = choose(word)
    if not d or not d.strokes:
        # Create placeholder
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

def main():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Word Draw Game")
    font = pygame.font.SysFont(None, FONT_SIZE)
    clock = pygame.time.Clock()
    
    # Load the pen sound as music (supports seeking)
    pen_sound_loaded = False
    try:
        pygame.mixer.music.load(SOUND_FILE)
        pen_sound_loaded = True
        print(f"Successfully loaded {SOUND_FILE}")
    except Exception as e:
        print(f"Warning: Could not load {SOUND_FILE}: {e}")

    items = []
    rects = []
    for w in random.sample(CATEGORIES, WORDS):
        it = build(w, font)
        it["pos"], r = random_pos(it["bounds"], rects)
        items.append(it)
        rects.append(r)

    buf = ""
    flash = None
    running = True
    
    while running:
        now = pygame.time.get_ticks()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and not flash:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_BACKSPACE:
                    buf = buf[:-1]
                elif e.key == pygame.K_SPACE:
                    # Allow spaces in input
                    buf += ' '
                else:
                    c = e.unicode.lower()
                    if c.isalpha():
                        buf += c
                        # Check if any word matches
                        for idx, it in enumerate(items):
                            if it["word"] == buf:
                                draw_speed = random.uniform(0.8, 1.2)
                                flash = dict(start=now, item=it, idx=idx, draw_speed=draw_speed)
                                
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
        
        if flash:
            it = flash["item"]
            elapsed = now - flash["start"]
            # Apply randomized drawing speed
            prog = min(1, (elapsed * flash["draw_speed"]) / FLASH_MS)
            
            if it["drawing"] and it["drawing"].strokes:
                # Render with animation progress
                big = render(it["drawing"].strokes, int(HEIGHT * 0.55), GREEN, BIG_W, progress=prog)
            else:
                big = pygame.Surface((int(HEIGHT * 0.55), int(HEIGHT * 0.55)), pygame.SRCALPHA)
                pygame.draw.rect(big, GREEN, big.get_rect(), BIG_W)
            
            screen.fill(BG)
            rect = big.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(big, rect)
            
            cap = font.render(it["word"].replace(' ', '_'), True, TEXT)
            screen.blit(cap, cap.get_rect(center=(WIDTH // 2, rect.bottom + CAP_PAD + cap.get_height() // 2)))
            
            pygame.display.flip()
            
            if prog >= 1:
                # Stop the music when drawing is complete
                pygame.mixer.music.stop()
                print("Stopped music")
                
                new_word = random.choice(CATEGORIES)
                new_it = build(new_word, font)
                pos, r = random_pos(new_it["bounds"], [pygame.Rect(i["pos"], i["bounds"]) for i in items if i != it])
                new_it["pos"] = pos
                items[flash["idx"]] = new_it
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
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()