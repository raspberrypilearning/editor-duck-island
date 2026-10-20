"""Small Scratch 3 writer used to keep this tutorial's examples and checkpoints aligned.

Only the blocks used by this project are supported. It does not parse arbitrary
Markdown or convert other tutorials automatically.
"""
import copy
import hashlib
import json
import zipfile


def svg_asset(name, drawing, width, height, assets):
    raw = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}">{drawing}</svg>').encode()
    aid = hashlib.md5(raw).hexdigest()
    assets[aid + ".svg"] = raw
    return dict(name=name, bitmapResolution=1, dataFormat="svg", assetId=aid,
                md5ext=aid + ".svg", rotationCenterX=width / 2, rotationCenterY=height / 2)


def sprite(name, costumes, sounds=(), **properties):
    return dict(isStage=False, name=name, variables={}, lists={}, broadcasts={},
                blocks={}, comments={}, currentCostume=0, costumes=copy.deepcopy(costumes),
                sounds=copy.deepcopy(list(sounds)), volume=100, layerOrder=1, visible=True,
                x=0, y=0, size=100, direction=90, draggable=False, rotationStyle="all around",
                **properties)


EXPRS = {
    "x": ("motion_xposition", [], []), "y": ("motion_yposition", [], []),
    "costume": ("looks_costumenumbername", [], [("NUMBER_NAME", "number")]),
    "key": ("sensing_keypressed", ["KEY_OPTION"], []),
    "touch": ("sensing_touchingobject", ["TOUCHINGOBJECTMENU"], []),
    "random": ("operator_random", ["FROM", "TO"], []),
    "gt": ("operator_gt", ["OPERAND1", "OPERAND2"], []),
    "lt": ("operator_lt", ["OPERAND1", "OPERAND2"], []),
    "eq": ("operator_equals", ["OPERAND1", "OPERAND2"], []),
    "and": ("operator_and", ["OPERAND1", "OPERAND2"], []),
    "or": ("operator_or", ["OPERAND1", "OPERAND2"], []),
    "not": ("operator_not", ["OPERAND"], []),
    "minus": ("operator_subtract", ["NUM1", "NUM2"], []),
    "plus": ("operator_add", ["NUM1", "NUM2"], []),
    "abs": ("operator_mathop", ["NUM"], [("OPERATOR", "abs")]),
}
CMDS = {
    "flag": ("event_whenflagclicked", [], []),
    "clone_start": ("control_start_as_clone", [], []),
    "clicked": ("event_whenthisspriteclicked", [], []),
    "receive": ("event_whenbroadcastreceived", [], ["BROADCAST_OPTION"]),
    "goto": ("motion_gotoxy", ["X", "Y"], []),
    "setx": ("motion_setx", ["X"], []), "sety": ("motion_sety", ["Y"], []),
    "dx": ("motion_changexby", ["DX"], []), "dy": ("motion_changeyby", ["DY"], []),
    "point": ("motion_pointindirection", ["DIRECTION"], []),
    "move_steps": ("motion_movesteps", ["STEPS"], []),
    "size": ("looks_setsizeto", ["SIZE"], []),
    "costume": ("looks_switchcostumeto", ["COSTUME"], []),
    "next": ("looks_nextcostume", [], []),
    "show": ("looks_show", [], []), "hide": ("looks_hide", [], []),
    "layer": ("looks_gotofrontback", [], ["FRONT_BACK"]),
    "wait": ("control_wait", ["DURATION"], []),
    "delete": ("control_delete_this_clone", [], []),
    "clone": ("control_create_clone_of", ["CLONE_OPTION"], []),
    "set": ("data_setvariableto", ["VALUE"], ["VARIABLE"]),
    "change": ("data_changevariableby", ["VALUE"], ["VARIABLE"]),
    "sound": ("sound_play", ["SOUND_MENU"], []),
    "sound_wait": ("sound_playuntildone", ["SOUND_MENU"], []),
    "volume": ("sound_setvolumeto", ["VOLUME"], []),
    "pitch": ("sound_seteffectto", ["VALUE"], ["EFFECT"]),
    "stop": ("control_stop", [], ["STOP_OPTION"]),
    "broadcast": ("event_broadcast", ["BROADCAST_INPUT"], []),
    "broadcast_wait": ("event_broadcastandwait", ["BROADCAST_INPUT"], []),
    "say": ("looks_sayforsecs", ["MESSAGE", "SECS"], []),
}
MENUS = {
    "KEY_OPTION": ("sensing_keyoptions", "KEY_OPTION"),
    "TOUCHINGOBJECTMENU": ("sensing_touchingobjectmenu", "TOUCHINGOBJECTMENU"),
    "CLONE_OPTION": ("control_create_clone_of_menu", "CLONE_OPTION"),
    "COSTUME": ("looks_costume", "COSTUME"),
    "SOUND_MENU": ("sound_sounds_menu", "SOUND_MENU"),
}


class Compiler:
    def __init__(self, target, stage):
        self.target, self.stage = target, stage
        self.blocks = {}
        self.count = 0
        self.warps = {}

    def add(self, opcode, parent=None, shadow=False):
        self.count += 1
        key = f"{self.target['name']}-{self.count}"
        self.blocks[key] = dict(opcode=opcode, next=None, parent=parent,
                                inputs={}, fields={}, shadow=shadow, topLevel=parent is None)
        return key

    def variable(self, name):
        for t in (self.target, self.stage):
            for key, (label, _) in t["variables"].items():
                if label == name:
                    return key
        raise ValueError(f"Undefined variable {name} on {self.target['name']}")

    def input(self, name, value, parent):
        if isinstance(value, tuple):
            if value[0] == "var":
                return [3, [12, value[1], self.variable(value[1])], [4, "0"]]
            opcode, names, fields = EXPRS[value[0]]
            key = self.add(opcode, parent)
            b = self.blocks[key]
            b["fields"] = {f: [v, None] for f, v in fields}
            for field, arg in zip(names, value[1:]):
                b["inputs"][field] = self.input(field, arg, key)
            if value[0] in ("key", "touch", "gt", "lt", "eq", "and", "or", "not"):
                return [2, key]
            return [3, key, [4, "0"]]
        if name in MENUS:
            opcode, field = MENUS[name]
            key = self.add(opcode, parent, True)
            self.blocks[key]["fields"][field] = [value, None]
            return [1, key]
        if name == "BROADCAST_INPUT":
            return [1, [11, value, "message-" + value]]
        return [1, [4 if isinstance(value, (int, float)) else 10, str(value)]]

    def chain(self, commands, parent=None):
        first, previous = None, None
        for cmd in commands:
            kind, *args = cmd
            if kind == "define":
                key = self.add("procedures_definition", previous or parent)
                proto = self.add("procedures_prototype", key, True)
                self.blocks[proto]["mutation"] = dict(tagName="mutation", children=[],
                    proccode=args[0], argumentids="[]", argumentnames="[]",
                    argumentdefaults="[]", warp=str(args[1]).lower())
                self.blocks[key]["inputs"]["custom_block"] = [1, proto]
            elif kind == "call":
                key = self.add("procedures_call", previous or parent)
                self.blocks[key]["mutation"] = dict(tagName="mutation", children=[],
                    proccode=args[0], argumentids="[]", warp=str(self.warps[args[0]]).lower())
            elif kind in ("forever", "repeat", "if", "ifelse"):
                opcode = {"forever": "control_forever", "repeat": "control_repeat",
                          "if": "control_if", "ifelse": "control_if_else"}[kind]
                key = self.add(opcode, previous or parent)
                b = self.blocks[key]
                if kind != "forever":
                    b["inputs"]["TIMES" if kind == "repeat" else "CONDITION"] = self.input(
                        "TIMES" if kind == "repeat" else "CONDITION", args.pop(0), key)
                for index, substack in enumerate(args):
                    sub = self.chain(substack, key)
                    if sub:
                        b["inputs"]["SUBSTACK" + ("2" if index else "")] = [2, sub]
            else:
                opcode, names, fields = CMDS[kind]
                key = self.add(opcode, previous or parent)
                b = self.blocks[key]
                for field in fields:
                    value = args.pop(0)
                    identity = self.variable(value) if field == "VARIABLE" else (
                        "message-" + value if field == "BROADCAST_OPTION" else None)
                    b["fields"][field] = [value, identity]
                for name, value in zip(names, args):
                    b["inputs"][name] = self.input(name, value, key)
                if kind == "stop":
                    b["mutation"] = dict(tagName="mutation", children=[], hasnext="false")
            if previous:
                self.blocks[previous]["next"] = key
            first = first or key
            previous = key
        return first

    def compile(self, scripts):
        self.warps = {s[0][1]: s[0][2] for s in scripts if s[0][0] == "define"}
        for index, script in enumerate(scripts):
            head = self.chain(script)
            self.blocks[head].update(x=40 + (index % 3) * 420, y=40 + (index // 3) * 550)
        self.target["blocks"] = self.blocks


def expr(value):
    if not isinstance(value, tuple):
        return str(value)
    op, *a = value
    a = [expr(v) for v in a]
    if op == "var": return f"({a[0]})"
    if op in ("x", "y"): return f"({op} position)"
    if op == "costume": return "(costume [number v])"
    if op == "key": return f"<key ({a[0]} v) pressed?>"
    if op == "touch": return f"<touching ({a[0]} v)?>"
    if op == "random": return f"(pick random ({a[0]}) to ({a[1]}))"
    if op == "abs": return f"([abs v] of ({a[0]}))"
    if op == "not": return f"<not {a[0]}>"
    if op in ("and", "or"): return f"<{a[0]} {op} {a[1]}>"
    if op in ("gt", "lt", "eq"):
        symbol = {"gt": ">", "lt": "<", "eq": "="}[op]
        return f"<({a[0]}) {symbol} ({a[1]})>"
    if op in ("minus", "plus"):
        return f"(({a[0]}) {'-' if op == 'minus' else '+'} ({a[1]}))"
    raise ValueError(op)


def blocks(commands, indent=0):
    out = []
    for cmd in commands:
        k, *raw = cmd
        a = [expr(v) if not isinstance(v, list) else v for v in raw]
        if k in ("forever", "repeat", "if", "ifelse"):
            if k == "forever": start, bodies = "forever", raw
            elif k == "repeat": start, bodies = f"repeat ({a[0]})", raw[1:]
            else: start, bodies = f"if {a[0]} then", raw[1:]
            out.append(" " * indent + start)
            out.extend(blocks(bodies[0], indent + 4).splitlines())
            if k == "ifelse":
                out.append(" " * indent + "else")
                out.extend(blocks(bodies[1], indent + 4).splitlines())
            out.append(" " * indent + "end")
            continue
        forms = {
            "flag": "when green flag clicked", "clone_start": "when I start as a clone",
            "clicked": "when this sprite clicked", "receive": "when I receive ({0} v)",
            "goto": "go to x: ({0}) y: ({1})", "setx": "set x to ({0})",
            "sety": "set y to ({0})", "dx": "change x by ({0})", "dy": "change y by ({0})",
            "point": "point in direction ({0})", "move_steps": "move ({0}) steps",
            "size": "set size to ({0}) %", "costume": "switch costume to ({0} v)",
            "next": "next costume", "show": "show", "hide": "hide",
            "layer": "go to [{0} v] layer", "wait": "wait ({0}) seconds",
            "delete": "delete this clone", "clone": "create clone of ({0} v)",
            "set": "set [{0} v] to ({1})", "change": "change [{0} v] by ({1})",
            "sound": "start sound ({0} v)", "sound_wait": "play sound ({0} v) until done",
            "volume": "set volume to ({0}) %", "pitch": "set [{0} v] effect to ({1})",
            "stop": "stop [{0} v]", "broadcast": "broadcast ({0} v)",
            "broadcast_wait": "broadcast ({0} v) and wait",
            "say": "say [{0}] for ({1}) seconds",
            "define": "define {0}", "call": "{0} :: custom",
        }
        for i, value in enumerate(raw):
            if isinstance(value, tuple) and a[i].startswith("(") and a[i].endswith(")"):
                a[i] = a[i][1:-1]
        if k == "clone" and a[0] == "_myself_":
            a[0] = "myself"
        line = forms[k].format(*a)
        # A reporter already supplies its rounded outline; avoid redundant nesting.
        while "((" in line and "))" in line:
            import re
            reduced = re.sub(r"\(\(([^()]*)\)\)", r"(\1)", line)
            if reduced == line: break
            line = reduced
        if k == "costume" and isinstance(raw[0], tuple):
            line = "switch costume to " + expr(raw[0])
        out.append(" " * indent + line)
    return "\n".join(out)


def write_project(path, project, scripts, assets):
    data = copy.deepcopy(project)
    stage = data["targets"][0]
    for target in data["targets"]:
        Compiler(target, stage).compile(scripts.get(target["name"], {}).values())
    required = {asset["md5ext"] for t in data["targets"]
                for asset in t["costumes"] + t["sounds"]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps(data, separators=(",", ":")))
        for key in sorted(required):
            z.writestr(key, assets[key])
