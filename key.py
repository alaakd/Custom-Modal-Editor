from typing import Callable, Optional, Iterable
import platform

class EchoDict(dict):
    """A default dictionary that will echo the key if there's no pair associated with it."""
    def __init__(self, src: Optional[Iterable] = None):
        if src:
            super().__init__(src)
        else:
            super().__init__()

    def __getitem__(self, k):
        if k in self:
            return super().__getitem__(k)
        else:
            return k


KEY_MAP = EchoDict([
    (chr(27), "esc"),
    (chr(127), "backspace"),
    (chr(13), "newline"),
    (chr(10), "newline"),
    ("\t", "tab")
])
    
            
def key_pressed_windows() -> str:
    import keyboard
    while True:
        e = keyboard.read_event()
        if e.event_type == keyboard.KEY_DOWN:
            if e.name is not None:
                return e.name

def key_pressed_macos() -> str:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return KEY_MAP[ch]


key_getter: Optional[Callable[[], str]] = None

def pressed():
    global key_getter
    if key_getter is None:
        match platform.system():
            case "Darwin":
                key_getter = key_pressed_macos
            case "Windows":
                key_getter = key_pressed_windows
    return key_getter()
    
