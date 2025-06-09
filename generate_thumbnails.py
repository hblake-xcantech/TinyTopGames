#!/usr/bin/env python3
"""
Thumbnail Generator for Tiny Top Games
=====================================

Developer tool to generate thumbnails for all games in the games/ directory.
Only regenerates thumbnails when game.py has been modified since last generation.

Features:
- Automatic game discovery in games/ directory
- Caches file modification times to avoid unnecessary regeneration
- Runs games in --screenshot mode to capture thumbnails
- Generates 320x240 PNG thumbnails
- Creates .thumbnail_cache.json to track generation status

Usage:
  python generate_thumbnails.py           # Generate all missing/outdated thumbnails
  python generate_thumbnails.py --force   # Force regenerate all thumbnails
  python generate_thumbnails.py --clean   # Remove cache and all thumbnails

Developer Workflow:
1. Create a new game in games/NEW_GAME/game.py
2. Run this script to generate thumbnail
3. Commit both game.py and thumbnail.png to repo
4. Thumbnails are displayed automatically in main_menu.py
"""

import json
import subprocess
import sys
import os
import argparse
from pathlib import Path
import hashlib

CACHE_FILE = ".thumbnail_cache.json"
THUMBNAIL_SIZE = (320, 240)

class ThumbnailCache:
    """Manages thumbnail generation cache"""
    
    def __init__(self):
        self.cache_file = Path(CACHE_FILE)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except Exception as e:
                print(f"Warning: Could not load cache file: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            self.cache_file.write_text(json.dumps(self.cache, indent=2))
        except Exception as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def _get_file_hash(self, file_path):
        """Get SHA256 hash of file contents"""
        try:
            return hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
        except Exception:
            return None
    
    def needs_update(self, game_name, game_py_path, thumbnail_path):
        """Check if thumbnail needs to be generated/updated"""
        # If thumbnail doesn't exist, definitely need to generate
        if not Path(thumbnail_path).exists():
            return True
        
        # Check if we have cache entry for this game
        if game_name not in self.cache:
            return True
        
        # Get current file hash
        current_hash = self._get_file_hash(game_py_path)
        if current_hash is None:
            return True
        
        # Compare with cached hash
        cached_info = self.cache[game_name]
        return cached_info.get('game_hash') != current_hash
    
    def mark_generated(self, game_name, game_py_path, thumbnail_path):
        """Mark thumbnail as generated for given game"""
        game_hash = self._get_file_hash(game_py_path)
        if game_hash:
            self.cache[game_name] = {
                'game_hash': game_hash,
                'thumbnail_path': str(thumbnail_path),
                'generated_at': str(Path(thumbnail_path).stat().st_mtime) if Path(thumbnail_path).exists() else None
            }
            self._save_cache()
    
    def clear_cache(self):
        """Clear all cache entries"""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()

def discover_games():
    """Discover all games that can have thumbnails generated"""
    games = []
    games_dir = Path("games")
    
    if not games_dir.exists():
        print("Error: games/ directory not found!")
        return games
    
    for game_dir in games_dir.iterdir():
        if not game_dir.is_dir():
            continue
            
        game_py = game_dir / "game.py"
        if not game_py.exists():
            print(f"Skipping {game_dir.name}: no game.py found")
            continue
        
        thumbnail_path = game_dir / "thumbnail.png"
        
        games.append({
            'name': game_dir.name,
            'game_py': str(game_py),
            'thumbnail_path': str(thumbnail_path),
            'directory': str(game_dir)
        })
    
    return games

def generate_thumbnail(game_info):
    """Generate thumbnail for a single game"""
    print(f"Generating thumbnail for {game_info['name']}...")
    
    try:
        # Run game in screenshot mode
        result = subprocess.run([
            sys.executable, game_info['game_py'], '--screenshot'
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            if Path(game_info['thumbnail_path']).exists():
                print(f"✓ Thumbnail generated: {game_info['thumbnail_path']}")
                return True
            else:
                print(f"✗ Game ran successfully but no thumbnail was created")
                return False
        else:
            print(f"✗ Game failed to run (exit code {result.returncode})")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ Game timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"✗ Error running game: {e}")
        return False

def clean_thumbnails(games):
    """Remove all thumbnails and cache"""
    print("Cleaning thumbnails and cache...")
    
    # Remove cache
    cache_file = Path(CACHE_FILE)
    if cache_file.exists():
        cache_file.unlink()
        print(f"✓ Removed cache file: {CACHE_FILE}")
    
    # Remove thumbnails
    removed_count = 0
    for game in games:
        thumbnail_path = Path(game['thumbnail_path'])
        if thumbnail_path.exists():
            thumbnail_path.unlink()
            print(f"✓ Removed thumbnail: {game['thumbnail_path']}")
            removed_count += 1
    
    print(f"Cleaned {removed_count} thumbnails")

def main():
    """Main thumbnail generation function"""
    parser = argparse.ArgumentParser(description='Generate thumbnails for Tiny Top Games')
    parser.add_argument('--force', action='store_true', 
                       help='Force regenerate all thumbnails')
    parser.add_argument('--clean', action='store_true',
                       help='Remove all thumbnails and cache')
    
    args = parser.parse_args()
    
    # Discover games
    games = discover_games()
    if not games:
        print("No games found to process!")
        return
    
    print(f"Found {len(games)} games: {[g['name'] for g in games]}")
    
    # Handle clean command
    if args.clean:
        clean_thumbnails(games)
        return
    
    # Initialize cache
    cache = ThumbnailCache()
    
    # Process each game
    generated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for game in games:
        # Check if we need to generate thumbnail
        if not args.force and not cache.needs_update(
            game['name'], game['game_py'], game['thumbnail_path']
        ):
            print(f"⏭  Skipping {game['name']}: thumbnail up to date")
            skipped_count += 1
            continue
        
        # Generate thumbnail
        if generate_thumbnail(game):
            cache.mark_generated(game['name'], game['game_py'], game['thumbnail_path'])
            generated_count += 1
        else:
            failed_count += 1
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  Generated: {generated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total games: {len(games)}")
    
    if generated_count > 0:
        print(f"\n✨ {generated_count} thumbnails generated successfully!")
        print(f"Run 'python main_menu.py' to see your games with thumbnails.")
    elif skipped_count == len(games):
        print(f"\n✅ All thumbnails are up to date!")
    
    if failed_count > 0:
        print(f"\n⚠️  {failed_count} games failed to generate thumbnails.")
        print(f"Make sure each game supports the --screenshot argument.")

if __name__ == "__main__":
    main() 