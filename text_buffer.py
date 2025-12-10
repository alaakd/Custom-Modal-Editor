from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Optional, Iterator


# ============================================================================
# Color
# ============================================================================

@dataclass
class Color:
    r: int
    g: int
    b: int

    def __str__(self) -> str:
        if not hasattr(self, "s"):
            self.s = f"rgb({self.r},{self.g},{self.b})"
        return self.s

    def __eq__(self, other: Color) -> bool:
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __hash__(self) -> int:
        return hash((self.r, self.g, self.b))

    @staticmethod
    def from_hex(s: str) -> Color:
        r = int(s[1:3], 16)
        g = int(s[3:5], 16)
        b = int(s[5:7], 16)
        return Color(r, g, b)


NO_COLOR = Color(-1, -1, -1)
REGULAR = Color(255, 255, 255)
CURSOR = Color(128, 128, 128)
REGION = Color(0, 255, 0)

# ============================================================================
# Character
# ============================================================================

@dataclass
class Character:
    char: str
    fg_color: Color = field(default_factory=lambda: REGULAR)
    bg_color: Color = field(default_factory=lambda: NO_COLOR)


# ============================================================================
# Text Buffer
# ============================================================================

T = TypeVar("T")

@dataclass
class DoubleLink[T]:
    element: T
    next: Optional[DoubleLink[T]] = None
    prev: Optional[DoubleLink[T]] = None


class TextBufferException(Exception):
    """Raised when there is a buffer error."""


class TextBuffer:
    """Store the buffers characters in a doubly-linked chain/list."""

    def __init__(self):
        eof = Character("\0")
        self.head= DoubleLink(eof)
        self.point = self.head
        self.mark = None

    def insert_at_point(self, char: Character):
        new_node = DoubleLink(char, next=self.point, prev=self.point.prev)
        if self.point.prev:
            self.point.prev.next = new_node
        else:
            self.head = new_node
        self.point.prev = new_node
        self.mark = None

    def delete_at_point(self):
        if self.point.prev is None:
            return  # Nothing to delete
        to_delete = self.point.prev
        if to_delete.prev:
            to_delete.prev.next = self.point
            self.point.prev = to_delete.prev
        else:
            self.head = self.point
            self.point.prev = None
        self.mark = None

    def forward_char(self):
        if self.point.next:
            self.point = self.point.next

    def backward_char(self):
        if self.point.prev:
            self.point = self.point.prev

    def set_mark(self):
        self.mark = self.point

    def kill_region(self):
        if not self.mark or self.mark == self.point:
            raise TextBufferException("No region to kill")

        start, end = (self.mark, self.point) if self._is_after(self.point, self.mark) else (self.point, self.mark)

        current = start
        while current != end:
            next_node = current.next
            if current.prev:
                current.prev.next = current.next
            else:
                self.head = current.next
            if current.next:
                current.next.prev = current.prev
            current = next_node

        self.point = end.next if end and end.next else self.head
        self.mark = None

    def _is_after(self, a: DoubleLink, b: DoubleLink) -> bool:
        current = b
        while current and current != a:
            current = current.next
        return current == a

    def __iter__(self) -> Iterator[tuple[Character, bool, bool]]:
        current = self.head
        while current:
            is_point = current == self.point
            in_region = False
            if self.mark and self.mark != self.point:
                in_region = self._in_region(current)
            yield (current.element, is_point, in_region)
            current = current.next

    def _in_region(self, node: DoubleLink) -> bool:
        if not self.mark or self.mark == self.point:
            return False

        if self._is_after(self.point, self.mark):
            # point after mark -> include [mark, point) -> exclude point
            current = self.mark
            while current and current != self.point:
                if current == node:
                    return True
                current = current.next
        else:
            # point before mark -> include [point, mark) -> exclude mark
            current = self.point
            while current and current != self.mark:
                if current == node:
                    return True
                current = current.next

        return False


