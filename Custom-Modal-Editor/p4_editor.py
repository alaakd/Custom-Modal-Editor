from __future__ import annotations

import sys

from typing import TypeVar, Iterator, Optional
from enum import Enum

from rich import box
from rich.console import Console
from rich.panel import Panel

import key

from text_buffer import TextBuffer, Color, Character, TextBufferException, NO_COLOR, CURSOR, REGION

DEBUG: bool = True
if DEBUG:
    debug_log = open("debug_editor.txt", "w")
    

console: Console = Console() #color_system="truecolor")


class Mode(Enum):
    """Enumeration for the editor's two modes of operation: command and insert."""
    INSERT, COMMAND = range(2)

    def __str__(self):
        return "insert" if self == Mode.INSERT else "command"


class EditorException(Exception):
    """Raised when there is an editor error."""

    
class Editor:
    """The illustrious Programming IV editor. A great combination of power from both vim and emacs."""
    
    def __init__(self, width: int, height: int, buffer: TextBuffer):
        
        self.buffer: TextBuffer = buffer
        
        self.height: int = height
        self.width: int = width

        self.mode: Mode = Mode.COMMAND
        self.message: Optional[str] = None
        self.is_quit: bool = False

    def set_mode(self, mode: Mode):
        self.mode = mode
        
    def print(self):
        console.print(self.get_panel())
        console.print(self.mode, end="")
        if self.message:
            console.print(f" [{self.message}]")
            self.message = None
        else:
            
            console.print()
        
    def key_pressed(self, key: str):
        """Key is pressed in the editor."""
        try:
            if self.mode == Mode.INSERT:
                self.insert(key)
            else:
                self.command(key)
        except (TextBufferException, EditorException) as e:
            message = str(e)

            
    def insert(self, key: str):
        """Process key-press in insert mode."""
        match key:
            case "esc":
                self.set_mode(Mode.COMMAND)
            case "tab":
                self.set_mode(Mode.COMMAND)
            case "backspace":
                self.buffer.delete_at_point()
            case "newline":
                self.buffer.insert_at_point(Character("\n"))
            case _:
                if key is not None and len(key) == 1:
                    self.buffer.insert_at_point(Character(key))

    def command(self, key: str):
        """Process key-press in command mode."""
        match key:
            case "i":
                self.set_mode(Mode.INSERT)
            case "j":
                self.buffer.backward_char()
            case "k":
                self.buffer.forward_char()
            # not for now
            # case "l":
            #     self.buffer.previous_line()
            # case ";":
            #     self.buffer.next_line()
            case "m":
                self.buffer.set_mark()
            case ",":
                self.buffer.kill_region()
            case "q":
                self.is_quit = True
            case _:
                raise EditorException(f"unknown command: {key}")

                
    def get_panel(self):
        """Construct the rich panel from the text buffer."""

        lines: list[str] = []
        
        line: str = ""
        line_pos: int = 0
        max_line_pos: int = 0

        # track current color to group color changes
        current_fg_color: Color = NO_COLOR
        current_bg_color: Color = NO_COLOR

        # cursor is displayed in the space directly _after_ point
        show_cursor: bool = False
        
        for i, (c, is_point, in_region) in enumerate(self.buffer):

            # add any foreground color change
            if c.fg_color != current_fg_color:
                if current_fg_color != NO_COLOR:
                    line += f"[/ {current_fg_color}]"
                if c.fg_color != NO_COLOR:
                    line += f"[{c.fg_color}]"
                current_fg_color = c.fg_color
             
            # background is used for cursor and region as well
            new_bg_color = c.bg_color
            if is_point:
                line += "[blink]"  # start the blinking
                new_bg_color = CURSOR
            elif in_region:
                new_bg_color = REGION

            # add any background color change
            if new_bg_color != current_bg_color:
                if current_bg_color != NO_COLOR:
                    line += f"[/ on {current_bg_color}]"
                if new_bg_color != NO_COLOR:
                    line += f"[on {new_bg_color}]"
                current_bg_color = new_bg_color

            # determine the actual char to display
            char_to_display: str = c.char
            if c.char == "\n" or c.char == "\0":
                if is_point:
                    char_to_display = " " # cursor needs a space to display when at newline
                else:
                    char_to_display = ""

            # append the character
            line += char_to_display
            line_pos += len(char_to_display)

            # append the line
            if line_pos >= self.width or c.char == "\n":
                lines.append(line)
                max_line_pos = max(max_line_pos, line_pos)
                line_pos = 0
                line = ""

            # reset the blink
            if is_point:
                line += f"[/blink]"
                

        # pad the last line to guarantee the width of the editor is as expected.
        max_line_pos = max(max_line_pos, line_pos)
        if max_line_pos < self.width:
            # close off any backgroud color first.
            if current_bg_color != NO_COLOR:
                line += f"[/ on {current_bg_color}]"
            line += " " * (self.width - line_pos)       
        lines.append(line)

        # TODO clip the lines to the window
        if len(lines) < self.height:
            lines = lines + ["" for i in range(self.height - len(lines))]

        rich_text: str = "\n".join(lines)
        if DEBUG:
            print(rich_text, file=debug_log)
            
        return Panel.fit(rich_text, box=box.ROUNDED)




def main(file_name: Optional[str] = None):

    buffer: TextBuffer = TextBuffer()

    # if provided, add the file contents to the buffer
    if file_name is not None:
        with open(file_name) as fh:
            for c in fh.read():
                buffer.insert_at_point(Character(c))
    
    editor: Editor = Editor(40, 10, buffer)
    while not editor.is_quit:
        editor.print()
        editor.key_pressed(key.pressed())



if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
