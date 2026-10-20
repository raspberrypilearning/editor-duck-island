"""Validate publication references and Scratch archive structure."""
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "en"
manifest = json.loads((ROOT / "conversion/manifest.json").read_text())
pages = manifest["pages"]
assert [p["step"] for p in pages] == list(range(1, len(pages) + 1))
assert len(list(EN.glob("step_*.md"))) == len(pages)
assert len(re.findall(r"^  - title:", (EN / "meta.yml").read_text(), re.M)) == len(pages)
assert {p["source"] for p in pages} == {f"step_{n}" for n in range(2, 13)}
for p in pages:
    text = (EN / f"step_{p['step']}.md").read_text()
    assert text.startswith("## " + p["title"] + "\n")
    assert p["target"] in {"player", "wave", "obstacle", "collectable", "hazard", "Stage", "game over"}
    assert all(0 < n < p["step"] for n in p["requires"])
    assert "## Now run your code" in text or "## Check your project" in text
    assert text.count("```") % 2 == 0
    assert "[!TASK]" not in text and "Matt Hogan" not in text
    assert "repeat until <>" not in text and "if <>" not in text
    for image in re.findall(r"\]\((images/[^)\s]+)\)", text):
        assert (EN / image).is_file(), image
for path in EN.rglob("*.sb3"):
    if path.name.startswith("._"):
        continue
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        data = json.loads(z.read("project.json"))
        targets = data["targets"]
        names = [t["name"] for t in targets]
        assert len(names) == len(set(names))
        assert "player" in names and "Matt Hogan" not in names
        globals_ = targets[0]["variables"]
        for target in targets:
            for asset in target["costumes"] + target["sounds"]:
                assert asset["md5ext"] in z.namelist(), asset
            blocks = target["blocks"]
            for identity, b in blocks.items():
                for key in ("next", "parent"):
                    assert b[key] is None or b[key] in blocks, (path, identity, key)
                for inp in b["inputs"].values():
                    for value in inp[1:]:
                        if isinstance(value, str): assert value in blocks, (path, identity, value)
                        if isinstance(value, list) and value[0] == 12:
                            assert value[2] in globals_ or value[2] in target["variables"]
                if "VARIABLE" in b["fields"]:
                    vid = b["fields"]["VARIABLE"][1]
                    assert vid in globals_ or vid in target["variables"]
        if "starter" in path.name:
            assert names == ["Stage", "player"]
            assert all(not t["blocks"] and not t["variables"] for t in targets)
        else:
            for name in ("collectable", "hazard"):
                t = next(t for t in targets if t["name"] == name)
                for b in t["blocks"].values():
                    if b["opcode"] == "data_setvariableto":
                        assert b["fields"]["VARIABLE"][0] != "rock speed"
                        if name == "hazard": assert b["fields"]["VARIABLE"][0] != "score"
for p in EN.glob("code/*/project_config.yml"):
    text = p.read_text()
    assert "type: 'code_editor_scratch'" in text and "build: true" in text
    assert p.parent.name in text
assert not list(EN.glob("code/**/main.py"))
print(f"PASS: {len(pages)} pages, source coverage, asset references, metadata, and Scratch archives.")
