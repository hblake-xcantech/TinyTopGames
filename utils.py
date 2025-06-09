import os
import sys
import pygame

THUMBNAIL_SIZE = (320, 240)


def screenshot_requested() -> bool:
    """Return True if a screenshot should be taken."""
    return "--screenshot" in sys.argv or os.environ.get("SCREENSHOT_MODE") == "1"


def check_screenshot(screen: pygame.Surface, output_path: str) -> None:
    """Save a scaled screenshot and exit if screenshot is requested."""
    if not screenshot_requested():
        return

    thumbnail = pygame.transform.scale(screen, THUMBNAIL_SIZE)
    pygame.image.save(thumbnail, output_path)
    print(f"Thumbnail saved to {output_path}")
    pygame.quit()
    sys.exit(0)
