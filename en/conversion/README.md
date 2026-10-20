# Duck Island conversion

## Baseline

- Source: `raspberrypilearning/duck-island`, **draft**, `375d8bf`.
- Destination: `raspberrypilearning/editor-duck-island`, **draft**.
- Starter: user-supplied `Duck island - starter.sb3`.
- User instruction: package the duck as **player**; do not ask learners to rename it.
- The original project is unchanged apart from switching to and pulling its draft branch.

`manifest.json` maps each page to its original section, editing target, expected
result, and completion milestone. Each original section is covered.

## Rules applied

Keep conversion tooling and reports under `en/conversion`. Do not add new
directories at the repository root; the publishing pipeline expects the
established root layout.

One page has one editing target (a sprite or Stage), one outcome, and a check
that works with the project built so far. A complete behaviour can need several
scripts. Empty conditions and uncalled custom blocks are not separate steps.
Artwork steps use visible checks; audio steps include an audible result.

Tests may exercise other existing sprites without editing them. Copying a
costume or duplicating a sprite leaves the source unchanged; subsequent edits
belong to the new target. Work shared between targets is separated into pages,
with monitors or direct script execution used to test the first half.

The core project is saved after step 31. The extension example includes all
optional features. The game-over connection requires its preceding sign page;
other extensions can be tried independently. The extra movement challenge is
a tuning exercise and does not change the example's default drift speed.

## Issues resolved before carrying their behaviour forward

| Source issue | Resolution |
|---|---|
| Local code folders contain template Python files | Replace them with actual Scratch starter/completed projects and editor configurations. |
| Supplied sprite name differs from later references | Normalise only the starter sprite name to `player`; retain costumes, sounds, initial properties, and code-free state. |
| `any key` starts swimming and spawning | Check the four arrow keys explicitly. Space is covered by runtime tests. |
| Tiny sprites may never reach ±240/±180 because of Scratch fencing | Spawn at x ±220/y ±160 and delete only after passing those bounds; use bounded, centred drawings. |
| Deletion depends on keys even when hooks drift on their own | Check position independently of keyboard input. |
| Costume contact can leave a duck overlapping rocks and unable to reverse | Probe 8 pixels ahead with a consistent `down` collision costume in a custom block running without screen refresh. Restore position and facing before drawing. Test approach and reversal in all four directions. |
| Local/global scope of blocked variables is unspecified | Four blocked variables and shared speed use “For all sprites”; saved facing uses “For this sprite only”. |
| Copied sprites inherit shared-state resets | Remove speed reset from collectable and score reset from hazard. Only obstacle owns speed reset; only collectable owns score reset. |
| Hook sound can be cut short by a fixed delay | Play its pitched pop until done before stopping. |
| Multi-sprite extension list | Separate extensions by target; split the game-over receiver and sender into two testable pages. |

The probe is the principal teaching change: it introduces a local saved-facing
variable and a custom block with screen refresh disabled. It is explained where
used, rather than relying on adjustment of costume centres to escape collisions.
Keep the shared world speed at 3 and probe distance at 8; higher speeds would
need renewed collision testing. Cosmetic duck costumes can extend beyond the
consistent collision shape.

The completed example uses simple SVG wave, rock, hook, and sign artwork
matching the drawing instructions. Duck costumes and audio come from the
supplied starter. Learner screenshots and the banner come from the source.

## Rebuild

From the repository root:

```sh
python3 en/conversion/build.py
python3 en/conversion/check_structure.py
```

`scratch_builder.py` serialises the supported Scratch blocks. `build.py`
contains the page prose, cumulative scripts, and example artwork. It renders
the same scripts into Markdown and `.sb3` files. Intermediate projects go to
`/private/tmp/editor-duck-island-checkpoints`; they are not publication assets.

This is authoring support, not an automatic long-form Markdown splitter.
The instructional outcome and dependency order still require editorial work.

## Runtime validation

The browser harness loads each core checkpoint in Scratch VM with the real
Scratch WebGL renderer and audio engine. It exercises keyboard input, clones,
costumes, movement, edge cleanup, collision escape, scoring, stopping, and
restart. It also checks extension scoring/lives/sign behaviour and renders every
`blocks3` example. Tests use simulated frame time and deterministic placements
of test clones to avoid waiting for randomly placed rocks to align.

Install validation-only dependencies outside this repository:

```sh
npm install --prefix /private/tmp/duck-island-tools \
  scratch-vm@5.0.300 scratch-render scratch-storage scratch-audio \
  scratchblocks esbuild playwright
/private/tmp/duck-island-tools/node_modules/.bin/esbuild \
  /private/tmp/duck-island-tools/node_modules/scratch-audio/dist.js \
  --bundle --platform=browser --format=iife --global-name=ScratchAudio \
  --outfile=/private/tmp/duck-island-tools/audio.js
node en/conversion/validate.cjs
```

The harness defaults to macOS Google Chrome. Override `DUCK_TEST_BROWSER` for a
different Chromium executable and `DUCK_TEST_TOOLS` for the dependency folder.
It serves files on localhost only and does not contact Scratch or GitHub.
`validation-results.json` records the result and `runtime-preview.png` shows
the rendered core game.

These checks exercise Scratch runtime behaviour. They do not confirm publishing,
the Raspberry Pi editor's full interface, or the remotely embedded demo.
