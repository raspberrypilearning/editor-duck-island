"""Rebuild the English editor tutorial and matching Scratch checkpoints.

Run from any directory: python3 en/conversion/build.py
Intermediate projects are written to /private/tmp/editor-duck-island-checkpoints.
The supplied starter is kept in en/code; its sprite is normalised to `player`.
"""
import copy
import difflib
import json
from pathlib import Path
import zipfile

from scratch_builder import blocks, sprite, svg_asset, write_project

ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / "en"
CHECKPOINTS = Path("/private/tmp/editor-duck-island-checkpoints")
STARTER = EN / "code/editor-duck-island-starter/editor-duck-island-starter.sb3"
COMPLETE = EN / "code/editor-duck-island-complete/editor-duck-island-complete.sb3"
with zipfile.ZipFile(STARTER) as z:
    project = json.loads(z.read("project.json"))
    assets = {n: z.read(n) for n in z.namelist() if n != "project.json"}
player = project["targets"][1]
player["name"] = "player"
assert not player["blocks"], "The starter must not contain the learner's code."
scripts = {"Stage": {}, "player": {}}
write_project(STARTER, project, scripts, assets)
project["meta"] = {"semver": "3.0.0", "vm": "5.0.300", "agent": "editor-duck-island"}
stage = project["targets"][0]
pages = []
previous_code = {}
icons = {"player": "player-sprite.png", "wave": "wave-sprite.png",
         "obstacle": "obstacle-sprite.png", "collectable": "colletable-sprite.png",
         "hazard": "hazard-sprite.png"}


def V(name): return ("var", name)
def key(direction): return ("key", direction + " arrow")
ARROWS = ("or", ("or", key("right"), key("left")), ("or", key("up"), key("down")))


def target(name):
    return next(t for t in project["targets"] if t["name"] == name)


def variable(name, value=0, owner="Stage", visible=False):
    t = target(owner)
    vid = owner + ":" + name
    t["variables"][vid] = [name, value]
    if not any(m["id"] == vid for m in project["monitors"]):
        project["monitors"].append(dict(id=vid, mode="default", opcode="data_variable",
            params={"VARIABLE": name}, spriteName=None if owner == "Stage" else owner,
            value=value, width=0, height=0, x=5,
            y=5 + 26 * sum(m["visible"] for m in project["monitors"]),
            visible=visible, sliderMin=0, sliderMax=100, isDiscrete=True))


def monitor(name, visible):
    for m in project["monitors"]:
        if m["params"]["VARIABLE"] == name: m["visible"] = visible


def script(name, label, commands):
    scripts.setdefault(name, {})[label] = commands
    return commands


def code(commands, old=None):
    text = blocks(commands)
    if old is not None:
        before = blocks(old).splitlines()
        after = text.splitlines()
        added = set()
        for tag, _, _, start, end in difflib.SequenceMatcher(a=before, b=after).get_opcodes():
            if tag in ("replace", "insert"): added.update(range(start, end))
        outlined_depth = None
        highlighted = []
        for i, line in enumerate(after):
            stripped = line.lstrip()
            depth = len(line) - len(stripped)
            covered = outlined_depth is not None
            if covered:
                # A new enclosing block already outlines everything inside it,
                # including both branches of an if/else.
                highlighted.append(line)
                if depth == outlined_depth and stripped == "end":
                    outlined_depth = None
                continue
            changed = i in added and stripped not in ("else", "end")
            highlighted.append(("+" if changed else "") + line)
            if changed and (stripped == "forever" or stripped.startswith(("if ", "repeat "))):
                outlined_depth = depth
        text = "\n".join(highlighted)
    return "```blocks3\n" + text + "\n```"


def page(title, who, source, instruction, example=None, test="", tip=None,
         check=False, challenge=False, milestone=None):
    number = len(pages) + 1
    icon = (f'![{who}.](images/{icons[who]})'
            '{:width="100px" height="100px" style="object-fit: contain;"}\n\n'
            if who in icons else "")
    text = f"## {title}\n\n{icon}{instruction.strip()}\n"
    if example: text += "\n" + example.strip() + "\n"
    if tip: text += "\n## Tip\n\n" + tip.strip() + "\n"
    text += "\n## " + ("Check your project" if check else "Now run your code") + "\n\n" + test.strip() + "\n"
    (EN / f"step_{number}.md").write_text(text)
    item = dict(step=number, title=title, target=who, source=source,
                requires=[number - 1] if number > 1 else [],
                test=test, challenge=challenge, milestone=milestone)
    pages.append(item)
    if not challenge:
        write_project(CHECKPOINTS / f"step_{number:02}.sb3", project, scripts, assets)
    return number


# PLAYER: every change runs immediately, including the deliberately partial turn.
setup = script("player", "setup", [
    ("flag",), ("layer", "front"), ("costume", "down"), ("size", 25), ("goto", 0, 0)])
page("Place your duck", "player", "step_2",
     """The starter project is open beside these instructions. It already contains **player**, your duck, with four direction costumes.

Select **player**. Add this script to put the duck in the middle of the water.""",
     code(setup),
     "Click the green flag. The duck faces down at the centre of the Stage. Drag it somewhere else, then click the flag again: it returns to the centre.")

turns = [("if", key("right"), [("costume", "right")])]
old = copy.deepcopy(setup)
setup.append(("forever", turns))
page("Turn right", "player", "step_2",
     "On **player**, add a `forever` loop below the starting position. Inside it, check the **right arrow** and switch to the **right** costume.",
     code(setup, old),
     "Click the flag, then press the right arrow. The duck turns right. It stays in the centre; later, the scenery will move around it.")
old = copy.deepcopy(setup)
for direction in ("left", "down", "up"):
    turns.append(("if", key(direction), [("costume", direction)]))
page("Turn in every direction", "player", "step_2",
     "On **player**, duplicate the right-arrow `if` block three times inside the same loop. Match each key to its costume.",
     code([("forever", turns)], [old[-1]]),
     "Press each arrow key separately. The duck faces right, left, down, and up when you press the matching key.",
     milestone="engaged")

idle = [("dy", 1), ("wait", 0.3), ("dy", -1), ("wait", 0.3)]
bob = script("player", "bob", [("flag",), ("forever", copy.deepcopy(idle))])
page("Bob on the water", "player", "step_3",
     "On **player**, start a second green-flag script. Move up a little, wait, then move back down and wait.",
     code(bob), "Click the flag and leave the keys alone. The duck gently bobs up and down without drifting away.")
old = copy.deepcopy(bob)
fast = [("dy", 3), ("wait", 0.1), ("dy", -3), ("wait", 0.1)]
bob[1] = ("forever", [("ifelse", ARROWS, fast, copy.deepcopy(idle))])
page("Bob faster when swimming", "player", "step_3",
     """On **player**, put the faster movement in an `if then else` block. Keep the gentle movement in `else`.

Join four `key pressed?` blocks using three `or` blocks. Check **only the arrow keys**.""",
     code(bob, old),
     "Hold an arrow key: the duck bobs faster. Release it: the gentle bob returns. Press space: the gentle bob should continue.")

# WAVE: costume creation is checked visually before animation uses it.
wave_costumes = [svg_asset("costume1",
    '<ellipse cx="55" cy="27" rx="34" ry="12" fill="none" stroke="#ffffff" stroke-width="3"/>',
    110, 54, assets)]
wave = sprite("wave", wave_costumes)
project["targets"].append(wave)
scripts["wave"] = {}
page("Draw a wave", "wave", "step_4",
     """Choose **Paint** from the sprite menu and name the new sprite **wave**.

Draw a wide oval with a white outline and no fill. Centre it on the paint editor's crosshair. Make it slightly wider than the duck.

![The Paint sprite option.](images/sprite-paint.png){:width="180"}

![Drawing a wave.](images/paint-wave.gif){:width="300"}""",
     test="Select the wave. You should see a white ring with water visible through its middle. Adjust the oval in the paint editor if it is much larger than the duck.", check=True)
wave_setup = script("wave", "setup", [
    ("flag",), ("layer", "back"), ("costume", "costume1"), ("goto", 0, -20)])
page("Put the wave under the duck", "wave", "step_4",
     "On **wave**, add a script to put the oval behind the duck and slightly below its centre.",
     code(wave_setup),
     "Click the flag. The ring sits around the duck's base. Move the wave elsewhere and restart: it returns underneath the duck.")
wave_idle = [("dy", -1), ("wait", 0.3), ("dy", 1), ("wait", 0.3)]
old = copy.deepcopy(wave_setup)
wave_setup.append(("forever", copy.deepcopy(wave_idle)))
page("Make the wave bob", "wave", "step_4",
     "On **wave**, add a loop to move the ring down and up. These movements go the opposite way to the duck's gentle bob.",
     code(wave_setup, old),
     "Click the flag and leave the keys alone. The wave and duck bob in opposite directions.")
for i, rx in [(2, 42), (3, 50)]:
    wave["costumes"].append(svg_asset(f"costume{i}",
        f'<ellipse cx="55" cy="27" rx="{rx}" ry="{12+i*3}" fill="none" stroke="#ffffff" stroke-width="3"/>',
        110, 54, assets))
page("Make three wave costumes", "wave", "step_4",
     """On **wave**, open **Costumes**. Duplicate the oval twice. Enlarge the second oval a little and the third a little more, keeping their centres aligned.

Name them **costume1**, **costume2**, and **costume3**, from smallest to largest.

![Enlarging the wave costumes.](images/animate-waves.gif){:width="300"}""",
     test="Stop the project. Click each costume thumbnail. The ring should grow in three steps while its centre stays in the same place.", check=True)
old = copy.deepcopy(wave_setup)
wave_setup[-1] = ("forever", [("ifelse", ARROWS,
    [("next",), ("wait", 0.1)], [("costume", "costume1"), *copy.deepcopy(wave_idle)])])
page("Animate the swimming wave", "wave", "step_4",
     "On **wave**, use the same four-arrow condition as the duck. While an arrow is held, change costume. Otherwise, return to the smallest ring and bob gently.",
     code(wave_setup, old),
     "Click the flag. Hold an arrow: the ring expands repeatedly. Release it: the smallest ring returns and gently bobs. Space should not animate the ring.")

# OBSTACLE: explicit drawing dimensions keep Scratch fencing bounds predictable.
rock = svg_asset("rock",
    '<path d="M3 29L12 10L29 3L49 11L57 30L43 39L14 39Z" fill="#66747d" stroke="#38434a" stroke-width="2"/>'
    '<path d="M13 12L29 5L46 12L30 18Z" fill="#89969e"/>', 60, 42, assets)
obstacle = sprite("obstacle", [rock], [stage["sounds"][0]])
project["targets"].append(obstacle)
scripts["obstacle"] = {}
page("Draw a rock", "obstacle", "step_5",
     """Paint a new sprite and name it **obstacle**.

Draw a grey rock, about **60 pixels wide and 40 pixels high**, centred on the paint editor's crosshair. Keep it on one costume called **rock**. Leave the sprite's Size at `100`.

![The Paint sprite option.](images/sprite-paint.png){:width="180"}""",
     test="Your rock appears on the Stage. It should be about the duck's width. Use the paint editor to resize the drawing if necessary.", check=True)
appear = script("obstacle", "appear", [
    ("define", "appear", False),
    ("goto", ("random", -200, 200), ("random", -140, 140)), ("show",)])
rock_setup = script("obstacle", "setup", [("flag",), ("hide",), ("clone", "_myself_")])
rock_clone = script("obstacle", "clone", [("clone_start",), ("call", "appear")])
page("Make one rock appear", "obstacle", "step_5",
     """On **obstacle**, choose **My Blocks → Make a Block** and name it **appear**. Leave **Run without screen refresh** unticked.

Build these three scripts. The original hides; its clone calls `appear` to move to a random position and show itself.""",
     "\n\n".join(code(s) for s in (rock_setup, appear, rock_clone)),
     "Click the flag several times. Each restart shows one rock at a new position. The duck and wave still work.",
     tip="A clone is a copy of a sprite. A custom block only runs when another script calls it.")
old = copy.deepcopy(appear)
appear.insert(-1, ("size", ("random", 50, 100)))
page("Vary the rock sizes", "obstacle", "step_5",
     "On **obstacle**, add a random size to `define appear`, before `show`.",
     code(appear, old),
     "Restart several times. The rock changes size as well as position. It should stay between half and all of the size you drew.")
old = copy.deepcopy(rock_setup)
rock_setup[-1] = ("forever", [("if", ARROWS, [
    ("clone", "_myself_"), ("wait", ("random", 1, 3))])])
page("Make rocks while swimming", "obstacle", "step_5",
     "On **obstacle**, replace the single `create clone` with a loop. Make a clone only while an arrow key is held, then wait between `1` and `3` seconds.",
     code(rock_setup, old),
     "Restart, then hold an arrow for a few seconds. Several rocks appear with gaps between them. Release the key: no new rocks should appear. Pressing space alone should not create rocks.",
     tip="Restart to clear the rocks. They will move and disappear in later steps; keep these early tests short.")

old = copy.deepcopy(appear)
appear.extend([("if", key("right"), [("setx", 220)]),
               ("if", key("left"), [("setx", -220)])])
page("Start rocks at the side edges", "obstacle", "step_6",
     "On **obstacle**, add two checks at the end of `define appear`. Right-arrow rocks start on the right; left-arrow rocks start on the left.",
     code(appear, old),
     "Restart and hold right: new rocks appear at the right edge. Restart and hold left: they appear at the left edge. They stay there for now.")
old = copy.deepcopy(appear)
appear.extend([("if", key("up"), [("sety", 160)]),
               ("if", key("down"), [("sety", -160)])])
page("Start rocks at the top and bottom", "obstacle", "step_6",
     "On **obstacle**, add two more checks to `define appear`. Use `y` for the top and bottom edges.",
     code(appear[-2:]),
     "Restart and hold up: rocks appear near the top. Restart and hold down: they appear near the bottom. Test one arrow key at a time.")

variable("rock speed", 3, visible=True)
rock_setup.insert(1, ("set", "rock speed", 3))
horizontal = [
    ("if", key("right"), [("dx", ("minus", 0, V("rock speed")))]),
    ("if", key("left"), [("dx", V("rock speed"))])]
movement = script("obstacle", "move", [("define", "move", False), *horizontal])
rock_clone.append(("forever", [("call", "move")]))
page("Move rocks sideways", "obstacle", "step_7",
     """On **obstacle**, make `rock speed` **For all sprites**. Keep its monitor visible and set it to `3` just below the green flag in the spawning script.

Make another custom block called **move**. Leave **Run without screen refresh** unticked. Build its definition, then call it repeatedly from the clone script.""",
     code(movement) + "\n\n" + code(rock_clone),
     "Restart and hold right. Rocks travel left across the water. Hold left: they travel right. Release the key: they stop.",
     tip="The duck stays near the centre. Moving the rocks the opposite way makes the duck look as if it is swimming.")
vertical = [
    ("if", key("up"), [("dy", ("minus", 0, V("rock speed")))]),
    ("if", key("down"), [("dy", V("rock speed"))])]
movement.extend(vertical)
page("Move rocks up and down", "obstacle", "step_7",
     "On **obstacle**, add these two checks below the sideways checks in `define move`.",
     code(vertical),
     "Restart and hold up. Rocks move down. Hold down: they move up. Try all four arrows separately and check that the scenery always moves opposite the duck's direction.")

disappear = script("obstacle", "disappear", [("define", "disappear", False),
    ("if", ("or", ("lt", ("x",), -220), ("gt", ("x",), 220)), [("delete",)])])
rock_clone[-1][1].append(("call", "disappear"))
page("Clear rocks at the side edges", "obstacle", "step_8",
     """On **obstacle**, make a custom block called **disappear**. Leave **Run without screen refresh** unticked.

Delete a clone when its x position goes beyond either side boundary. Call `disappear` after `move` inside the clone loop.""",
     code(disappear) + "\n\n" + code(rock_clone),
     "Restart and hold right until rocks cross the Stage. They disappear near the left edge. Restart and hold left to check the opposite edge.",
     tip="Use strict comparisons with `-220` and `220`. Clones start exactly on those boundaries and disappear after moving past them. These reachable positions avoid small sprites getting stuck at Scratch's outer edge.")
disappear.append(("if", ("or", ("lt", ("y",), -160), ("gt", ("y",), 160)), [("delete",)]))
page("Clear rocks at every edge", "obstacle", "step_8",
     "On **obstacle**, add a second check to `define disappear`. Check `y position` against `-160` and `160`.",
     code(disappear),
     "Restart and swim up, down, left, and right. Rocks disappear after passing any boundary. Release the keys: rocks still inside the water stay where they are.",
     tip="These checks use position, not which key is held. They will also work for hazards that drift by themselves.")

# The remaining pages are added below; each checkpoint is built from the same
# script structures rendered in its code examples.
variable("facing", 2, "player")
variable("right blocked", "no", visible=True)


def probe(direction):
    axis, offset = {"right": ("dx", 8), "left": ("dx", -8),
                    "up": ("dy", 8), "down": ("dy", -8)}[direction]
    return [(axis, offset),
            ("ifelse", ("touch", "obstacle"),
             [("set", direction + " blocked", "yes")],
             [("set", direction + " blocked", "no")]),
            (axis, -offset)]


checks = script("player", "checks", [("define", "check rocks", True),
    ("set", "facing", ("costume",)), ("costume", "down"),
    *probe("right"), ("costume", V("facing"))])
checking = script("player", "checking", [("flag",), ("forever", [("call", "check rocks")])])
page("Sense a rock on the right", "player", "step_9",
     """Select **player**. Make `right blocked` **For all sprites** and leave its monitor visible. Make `facing` **For this sprite only** and untick its monitor.

Make a custom block called **check rocks**. Tick **Run without screen refresh**.

The block remembers the current costume, uses **down** as a consistent collision shape, and briefly checks `8` pixels to the right. It returns to its original position and costume before the screen is drawn.""",
     code(checks) + "\n\n" + code(checking),
     "Restart and steer a rock towards the duck from the right. Watch `right blocked`: it changes from `no` to `yes` when the rock is close. Rocks can still pass through for now.",
     tip="The probe does not move the duck across the water. Every move is immediately undone. The `facing` variable lets the duck keep facing the direction you chose.")
variable("left blocked", "no", visible=True)
checks[-1:-1] = probe("left")
page("Sense a rock on the left", "player", "step_9",
     """On **player**, make `left blocked` **For all sprites**, with its monitor visible.

Add this group inside `define check rocks`, **before** the final `switch costume to facing`. It checks left, then returns to the centre.""",
     code(probe("left")),
     "Restart. Steer a rock towards the duck from the left. `left blocked` changes to `yes` as it approaches, then back to `no` after it passes. The duck should not drift sideways.")
for direction in ("up", "down"):
    variable(direction + " blocked", "no", visible=True)
checks[-1:-1] = [*probe("up"), *probe("down")]
page("Sense rocks above and below", "player", "step_9",
     """On **player**, make `up blocked` and `down blocked` **For all sprites**. Leave both monitors visible.

Add these two groups inside `define check rocks`, before the final costume-restoring block. Use `change y`, rather than `change x`.""",
     code([*probe("up"), *probe("down")]),
     "Restart and steer rocks above and below the duck. The matching monitor changes to `yes` when a rock is close. Move away and it returns to `no`; the duck still bobs around the centre.")

movement[1:] = [
    ("if", ("and", key(direction), ("eq", V(direction + " blocked"), "no")),
     body)
    for direction, (_, _, body) in zip(("right", "left", "up", "down"), [*horizontal, *vertical])
]
for name in ("rock speed", "right blocked", "left blocked", "up blocked", "down blocked"):
    monitor(name, False)
page("Stop at rocks", "obstacle", "step_9",
     """Select **obstacle**. In `define move`, join each arrow condition to its matching blocked variable with `and`.

Only move when that direction is **not blocked**. The variables must be **For all sprites**, so obstacle can read them.

Untick the `rock speed` and four blocked-variable monitors when you have checked the result.""",
     code(movement),
     "Restart and steer towards a rock. It stops just before reaching the duck. Press the opposite arrow: you can swim away. Test approaches from all four directions.",
     tip="The check looks slightly ahead, leaving space to reverse. Do not change the probe distances while testing. Keep `rock speed` at `3`.")

# COLLECTABLE: duplication changes the new target only. Shared speed is owned by
# obstacle, and score is owned by collectable, so copied resets are removed.
collectable = copy.deepcopy(obstacle)
collectable.update(name="collectable", blocks={})
collectable["costumes"] = [copy.deepcopy(player["costumes"][1])]
project["targets"].append(collectable)
scripts["collectable"] = copy.deepcopy(scripts["obstacle"])
scripts["collectable"]["setup"] = [
    c for c in scripts["collectable"]["setup"] if c[:2] != ("set", "rock speed")]
scripts["collectable"]["appear"] = [
    ("size", 15) if c[0] == "size" else c for c in scripts["collectable"]["appear"]]
page("Add a lost duck", "collectable", "step_10",
     """Duplicate **obstacle** and rename the copy **collectable**. From now on, edit only **collectable**.

Replace its rock costume with a duck. You can drag the **down** costume from player's Costumes tab onto collectable's thumbnail; this copies it without changing player. Delete the copied rock costume.

In collectable's `appear` block, replace the random size with `set size to 15%`. Delete `set rock speed to 3` from its green-flag script: obstacle already sets that shared value.""",
     test="Restart and hold an arrow. Small ducks appear among the rocks and travel across the water. They are scenery for now; touching one does not score.",
     tip="If you draw a different duck, adjust its size so it is clearly smaller than player.")
variable("score", 0, visible=True)
collect_setup = scripts["collectable"]["setup"]
collect_setup.insert(1, ("set", "score", 0))
page("Show a rescue score", "collectable", "step_10",
     """On **collectable**, make `score` **For all sprites** and leave its monitor ticked.

Add `set score to 0` immediately below the green flag in its spawning script. Drag the score monitor to the top-left of the Stage.""",
     code(collect_setup),
     "Click the flag. A score of `0` appears at the top-left. It stays at zero until you add the rescue rule next.")
rescue = ("if", ("touch", "player"), [("change", "score", 1), ("delete",)])
collect_clone = scripts["collectable"]["clone"]
collect_clone[-1][1].append(rescue)
page("Rescue a duck", "collectable", "step_10",
     "On **collectable**, add a touching check inside the clone's loop, after `disappear`. Add one point and delete that clone when it touches **player**.",
     code(collect_clone),
     "Restart and swim into a small duck. It disappears and the score increases by exactly `1`. A rock should never award a point.")
rescue[2].insert(1, ("sound", "pop"))
page("Hear each rescue", "collectable", "step_10",
     """On **collectable**, open **Sounds**. The painted sprite you duplicated should include **pop**. If it is missing, choose **Pop** from the sound library.

Return to **Code** and add `start sound pop` before deleting a rescued clone.""",
     code([rescue]),
     "Rescue a small duck. You hear a pop as it disappears, and the score still increases by one.",
     tip="Use `start sound` so the clone can disappear immediately.")

# HAZARD: retain no score reset or score change on the new sprite.
hazard = copy.deepcopy(collectable)
hazard.update(name="hazard", blocks={})
hazard["costumes"] = [svg_asset("hook",
    '<path d="M30 3V39C30 62 5 61 8 40L14 46" fill="none" stroke="#26343d" '
    'stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>',
    42, 66, assets)]
project["targets"].append(hazard)
scripts["hazard"] = copy.deepcopy(scripts["collectable"])
hazard_setup = scripts["hazard"]["setup"]
hazard_setup[:] = [c for c in hazard_setup if c[:2] != ("set", "score")]
hazard_appear = scripts["hazard"]["appear"]
hazard_appear[:] = [("size", 70) if c[0] == "size" else c for c in hazard_appear]
hazard_clone = scripts["hazard"]["clone"]
hazard_hit = hazard_clone[-1][1][-1]
hazard_hit[2][:] = [("delete",)]
page("Add a hook", "hazard", "step_11",
     """Duplicate **collectable** and rename the copy **hazard**. Edit only **hazard**.

Replace the duck costume with a painted hook, about `40` pixels wide and `65` pixels high, centred on the crosshair. In `appear`, set its size to `70%`.

Delete the copied `set score to 0` block from hazard's green-flag script. In its touching check, remove **both** `change score by 1` and `start sound pop`, leaving `delete this clone`.""",
     code([hazard_hit]),
     "Restart. Hooks appear alongside ducks and rocks. Touch a hook: it disappears without increasing the score. Rescue a duck: that still adds one point.",
     tip="Only collectable resets and changes the score. A duplicated sprite copies all its scripts, including resets.")
hazard_hit[2][:] = [("pitch", "PITCH", -30), ("sound_wait", "pop"), ("stop", "all")]
page("End the game on a hook", "hazard", "step_11",
     """On **hazard**, replace `delete this clone` in the touching check with these blocks.

Use **Sound → set pitch effect to -30** to lower the pop, then play it until done before stopping the game.""",
     code([hazard_hit]),
     "Restart and touch a hook. You hear a lower pop, then everything stops. The score must not increase for the hook. Click the flag to start a new game.")
hazard_appear.append(("point", ("random", -180, 180)))
hazard_clone[-1][1].insert(1, ("move_steps", 1))
page("Make hooks drift", "hazard", "step_11",
     """On **hazard**, add `point in direction (pick random -180 to 180)` at the end of `define appear`.

In the clone loop, add `move 1 steps` after your custom `move` block and **before** `disappear`. This extra movement continues when no arrow is held.""",
     code(hazard_clone),
     "Restart and hold an arrow to create hooks. Release it: rocks and small ducks stop, but hooks keep drifting. Hooks that cross a boundary disappear; touching one still ends the game.",
     tip="Some hooks point outwards and leave quickly. Others drift across the water. Keeping the extra speed at `1` leaves time to dodge them.",
     milestone="internal")

CORE_STEPS = len(pages)
write_project(COMPLETE, project, scripts, assets)

# Optional extensions retain the original ideas but each edits one target.
# They are specified and built in sequence for reproducible extension checks.
obstacle["costumes"].append(svg_asset("pale rock",
    '<path d="M4 32L17 7L38 4L56 24L49 39L11 40Z" fill="#a7b7c2" stroke="#4c6270" stroke-width="2"/>',
    60, 42, assets))
appear.insert(1, ("costume", ("random", 1, 2)))
page("Challenge: vary the rocks", "obstacle", "step_12",
     """On **obstacle**, add a second rock costume of a similar size. At the start of `define appear`, add:

```blocks3
switch costume to (pick random (1) to (2))
```

Leave the costumes on collectable and hazard alone.""",
     test="Restart and swim for a while. Both kinds of rock appear. Check that both still block the duck and disappear at the edges.", challenge=True)
script("Stage", "music", [("flag",), ("volume", 25),
    ("forever", [("sound_wait", "Drip Drop")])])
page("Challenge: add water sounds", "Stage", "step_12",
     """Select the **Stage**. Its Sounds tab already contains **Drip Drop**.

Add a quiet sound loop to play while you swim.""",
     code(scripts["Stage"]["music"]),
     "Restart. Water sounds loop quietly while you play. You can still hear rescues and the hook sound.", challenge=True)
variable("high score", 0, visible=True)
rescue[2].insert(1, ("if", ("gt", V("score"), V("high score")),
                    [("set", "high score", V("score"))]))
page("Challenge: remember your best score", "collectable", "step_12",
     """On **collectable**, make `high score` **For all sprites** and show its monitor. Do **not** reset it in the green-flag script.

Inside the rescue check, compare the scores **after** adding the point and **before** deleting the clone.""",
     code([rescue]),
     "Rescue some ducks, then restart. `score` returns to zero but `high score` keeps your best result. Beat it and watch it increase.", challenge=True)
variable("lives", 3, visible=True)
hazard_setup.insert(1, ("set", "lives", 3))
hazard_hit[2][:] = [("change", "lives", -1), ("pitch", "PITCH", -30),
    ("sound_wait", "pop"),
    ("ifelse", ("eq", V("lives"), 0), [("stop", "all")], [("delete",)])]
page("Challenge: give the duck three lives", "hazard", "step_12",
     """On **hazard**, make `lives` **For all sprites** and show its monitor. Set it to `3` just below hazard's green flag.

Replace the hook's touching response with this code. Each hook takes one life. Delete a hook after a non-final hit so it cannot take another life.""",
     code([hazard_hit]),
     "Restart and touch one hook at a time. Lives go from 3 to 2 to 1, and each hook disappears. The third hit stops the game. Restart: lives return to 3.", challenge=True)

gameover = sprite("game over", [svg_asset("game over",
    '<rect x="2" y="2" width="336" height="96" rx="18" fill="#173f5f" stroke="#ffffff" stroke-width="4"/>'
    '<text x="170" y="62" text-anchor="middle" font-family="sans-serif" font-size="42" fill="white">Game over</text>',
    340, 100, assets)])
project["targets"].append(gameover)
scripts["game over"] = {}
end_setup = script("game over", "setup", [("flag",), ("hide",)])
end_show = script("game over", "show", [
    ("receive", "game over"), ("goto", 0, 0), ("layer", "front"), ("show",)])
stage["broadcasts"]["message-game over"] = "game over"
page("Challenge: draw a game-over sign", "game over", "step_12",
     """Paint a new sprite called **game over** with a clear “Game over” message.

Add these scripts. Create a new broadcast message called **game over** in the receiver's menu.""",
     code(end_setup) + "\n\n" + code(end_show),
     "Click the green flag: the sign hides. Click the `when I receive game over` stack directly in the code area: the sign appears in front of the game. Restart to hide it again.",
     tip="The sign is ready to receive a message. The next challenge connects the hook to it.", challenge=True)

final_branch = hazard_hit[2][-1][2]
final_branch.insert(0, ("broadcast_wait", "game over"))
page("Challenge: show the sign at game over", "hazard", "step_12",
     """Complete **Draw a game-over sign** first.

On **hazard**, add `broadcast game over and wait` immediately **before** `stop all`. If you added lives, put it inside the final-life branch.

The `and wait` gives the sign time to appear before scripts stop.""",
     code([("broadcast_wait", "game over"), ("stop", "all")]),
     "Restart and lose the game. The sign appears before everything stops. Restart again: the sign hides and you can play another round.", challenge=True)
page("Challenge: tune the movement", "hazard", "step_12",
     """On **hazard**, change only the extra `move 1 steps` block in the clone loop. Try `0.5` for a slower drift or `1.5` for a faster drift.

Keep the shared `rock speed` and the duck's collision probes unchanged.""",
     test="Restart and create a few hooks, then release the arrows. Compare their drift with the earlier speed. Choose a speed that gives you time to dodge. Check that hooks still disappear at the edges.\n\nSave your project.",
     challenge=True, milestone="external")

# Finish packaging. Optional additions have their own example project; the main
# completed project remains the result of the required making steps.
write_project(EN / "solutions/editor-duck-island-with-challenges.sb3", project, scripts, assets)
for number, prerequisites in {32: [24], 33: [1], 34: [28], 35: [30],
                              36: [1], 37: [30, 36], 38: [31]}.items():
    pages[number - 1]["requires"] = prerequisites
manifest = dict(source_repository="https://github.com/raspberrypilearning/duck-island",
    source_branch="draft", source_commit="375d8bf", core_steps=CORE_STEPS,
    starter="User-supplied Duck island - starter.sb3; only sprite name normalised to player",
    pages=pages)
(ROOT / "en/conversion/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
meta = [
    "title: Duck island", "hero_image: images/banner.png",
    "description: Make a duck-rescue game in this Code Club arcade project.",
    "listed: false", "pdf: false", "landing: true", "steps:"]
for item in pages:
    meta.append("  - title: " + json.dumps(item["title"]))
    if item["challenge"]: meta.append("    challenge: true")
    if item["milestone"]: meta.extend(["    completion:", "      - " + item["milestone"]])
(EN / "meta.yml").write_text("\n".join(meta) + "\n")
for suffix, label in [("starter", "starter"), ("complete", "completed")]:
    directory = EN / "code" / f"editor-duck-island-{suffix}"
    (directory / "project_config.yml").write_text(
        f'name: "Duck island {label}"\nidentifier: "editor-duck-island-{suffix}"\n'
        "type: 'code_editor_scratch'\nbuild: true\n")
for f in EN.glob("step_*.md"):
    if int(f.stem.split("_")[1]) > len(pages): f.unlink()
print(f"Built {CORE_STEPS} core pages and {len(pages) - CORE_STEPS} optional pages.")
