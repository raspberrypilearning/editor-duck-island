## Make one rock appear

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, choose **My Blocks → Make a Block** and name it **appear**. Leave **Run without screen refresh** unticked.

Build these three scripts. The original hides; its clone calls `appear` to move to a random position and show itself.

```blocks3
when green flag clicked
hide
create clone of (myself v)
```

```blocks3
define appear
go to x: (pick random (-200) to (200)) y: (pick random (-140) to (140))
show
```

```blocks3
when I start as a clone
appear :: custom
```

## Tip

A clone is a copy of a sprite. A custom block only runs when another script calls it.

## Now run your code

Click the flag several times. Each restart shows one rock at a new position. The duck and wave still work.
