## Clear rocks at the side edges

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, make a custom block called **disappear**. Leave **Run without screen refresh** unticked.

Delete a clone when its x position goes beyond either side boundary. Call `disappear` after `move` inside the clone loop.

```blocks3
define disappear
if <<((x position)) < (-220)> or <((x position)) > (220)>> then
    delete this clone
end
```

```blocks3
when I start as a clone
appear :: custom
forever
    move :: custom
    disappear :: custom
end
```

## Tip

Use strict comparisons with `-220` and `220`. Clones start exactly on those boundaries and disappear after moving past them. These reachable positions avoid small sprites getting stuck at Scratch's outer edge.

## Now run your code

Restart and hold right until rocks cross the Stage. They disappear near the left edge. Restart and hold left to check the opposite edge.
