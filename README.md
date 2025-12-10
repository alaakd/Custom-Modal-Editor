


# Editor

By now you are all familiar with the infamous Editor War <https://en.wikipedia.org/wiki/Editor_war><sup><a id="fnr.1" class="footref" href="#fn.1" role="doc-backlink">1</a></sup>. Let's join in and add our own editor: `p4_editor`. We'll use a few features from `emacs` and `vi`:

-   A *modal* editing system with **insert** and **command** modes. This is how you edit in `vi`, or `emacs`'s `evil-mode`.

-   A system for text *buffers* (text stored in memory).

-   The way `emacs` marks regions and "kills" (cuts) them.

Warning: some of this assignment will be part of the course project. As a bare minimum, inserting characters and iterating over a buffer to display the text will be needed.


## Modes


### **Command** mode

The **command** mode is for moving around the cursor (called the *insertion point* or *point*) and defining the selected *region*. The following keys are bound to actions:

| key | action             | description                                            |
|-----|--------------------|--------------------------------------------------------|
| `i` | `set_mode(INSERT)` | Switch to **insert** mode.                             |
| `j` | `backward_char`    | Move the insertion point backwards in the buffer.      |
| `k` | `forward_char`     | Move the insertion point forwards in the buffer.       |
| `m` | `set_mark`         | Set the region mark to be the current insertion point. |
| `,` | `kill_region`      | Kill (a.k.a cut) the current region.                   |
| `q` | `quit`             | Quit the editor.                                       |

### **Insert** mode

The **insert** mode is for making buffer edits. The following keys are bound to actions:

| key         | action              | description                                           |
|-------------|---------------------|-------------------------------------------------------|
| `esc`       | `set_mode(COMMAND)` | Switch to **command** mode.                           |
| `backspace` | `delete_at_point`   | Delete the character just before the insertion point. |
| `<key>`     | `insert_at_point`   | Insert the character `<key>` at the insertion point.  |

If `esc` doesn't work in your terminal, you can also use `tab` to leave insert mode.


## Insertion point (aka *point*)

<style>
.point{
    animation: blinker 1s linear infinite;
    background-color:rgb(128,128,128);
}
.region{
    background-color:rgb(0,255,0);
}
@keyframes blinker {
  50% {
    opacity: 0;
  }
}
</style>

Point is displayed as blinking text on a grey background:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

Note: the text ends with the string termination character `\0`. It indicates the end-of-file (EOF) and won't be displayed in the editor.


### Forward movement (`forward_char`)

The `forward_char` command will move point forward once. So:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

after `forward_char` will be:

<code>Lorem ip<span class="point">s</span>um dolor sit amet\0</code>


### Backward movement (`backward_char`)

The `backward_char` command will move point backward once. So:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

after `backward_char` will be:

<code>Lorem <span class="point">i</span>psum dolor sit amet\0</code>


### Inserting a character at point (`insert_at_point`)

Characters are inserted *before* the insertion point. If we start with:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

and we do `insert_at_point("a")`, this will result in:

<code>Lorem ia<span class="point">p</span>sum dolor sit amet\0</code>


### Deleting a character at point (`delete_at_point`)

Characters are deleted *before* the insertion point. If we start with:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

and we do `delete_at_point()`, this will result in:

<code>Lorem <span class="point">p</span>sum dolor sit amet\0</code>


## Defining a region with mark and point


### Setting *mark* (`set_mark`)

When the mark is set (`set_mark`), initially there is no visible difference in the editor:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

but we we move forward, the *mark* and all positions between *mark* and *point* will be show with a colored background:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

<code>Lorem i<span class="region">p</span><span class="point">s</span>um dolor sit amet\0</code>

<code>Lorem i<span class="region">ps</span><span class="point">u</span>m dolor sit amet\0</code>

<code>Lorem i<span class="region">psu</span><span class="point">m</span> dolor sit amet\0</code>

This works with movement in the other direction as well:

<code>Lorem i<span class="point">p</span>sum dolor sit amet\0</code>

<code>Lorem <span class="point">i</span><span class="region"></span>psum dolor sit amet\0</code>

<code>Lorem<span class="point"> </span><span class="region">i</span>psum dolor sit amet\0</code>

<code>Lore<span class="point">m</span><span class="region"> i</span>psum dolor sit amet\0</code>

Be careful: when point is *past* mark, the region does **not** include the character at point but does include mark. However, when point is *before* mark, the character at point **is** included, but the mark isn't.


### Removing mark

Mark is removed whenever a edit command is run: `insert_at_point`, `delete_at_point` and `kill_region`.

### Killing text (aka cut)

When a region is active (the *mark* is set), the command `kill_region` will remove all characters in the region. For example:

<code>Lore<span class="point">m</span><span class="region"> i</span>psum dolor sit amet\0</code>

will become:

<code>Lore<span class="point">p</span>sum dolor sit amet\0</code>


## Text Buffer

The editor loads and displays text that is stored in a *buffer*. In `p4_editor`, this will be a double-linked list, which supports fast insertion and deletion.


### Characters

Each character in the buffer contains three pieces of information:

1.  The character as a `str`. The last character in the buffer is the *null* character  `"\0"` which represents EOF (end-of-file).
2.  The foreground color as RGB value.
3.  The background color as RGB value. The special constant `NO_COLOR` will turn off background color.


### Double linked list

Implement the class `TextBuffer` as a chain of double-links (a.k.a. a doubly-linked list).

```python
T = TypeVar("T")

@dataclass
class DoubleLink[T]:
    element: T
    next: Optional[DoubleLink[T]] = None
    prev: Optional[DoubleLink[T]] = None
```

The `next`'s are linked in the "forward" direction as we did in class. The `prev`'s are linked the other way, making a chain that you can move in either direction.

### Empty text buffer.

When the text buffer is empty, there is a single double-link containing the EOF character (`\0`). Point will be at this link, and there is no mark.

### Iterator

The provided `Editor` requires that `TextBuffer` is iterable, specifically that it provides an iterator of the form:

```python
def __iter__(self) -> Iterator[tuple[Character, bool, bool]]
```

The tuple returned by `__next__`: contains:

1.  The next character.
2.  Whether the character is *point* (True/False).
3.  Whether the character is in the *region* (True/False).


## Running in Pycharm

To run the editor inside pycharm you will need to setup a _run configuration_ and enable the option `Emulate terminal in output console`:

![](./images/run_config.png)

## Requirements

Implement the operations on the class `TextBuffer` as described above, to work with the `Editor` class. 

- `__iter__` and `__next__`
- `backward_char` and `forward_char`
- `delete_at_point` and `insert_at_point`
- `set_mark` and `kill_region`

Use double-links to store character data as described above.

## Footnotes

<sup><a id="fn.1" href="#fnr.1">1</a></sup> : Of course, we all know `emacs` will win.
