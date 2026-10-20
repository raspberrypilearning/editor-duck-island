## Move rocks sideways

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, make `rock speed` **For all sprites**. Keep its monitor visible and set it to `3` just below the green flag in the spawning script.

Make another custom block called **move**. Leave **Run without screen refresh** unticked. Build its definition, then call it repeatedly from the clone script.

```blocks3
define move
if <key (right arrow v) pressed?> then
    change x by ((0) - (rock speed))
end
if <key (left arrow v) pressed?> then
    change x by (rock speed)
end
```

```blocks3
when I start as a clone
appear :: custom
forever
    move :: custom
end
```

## Tip

The duck stays near the centre. Moving the rocks the opposite way makes the duck look as if it is swimming.

## Now run your code

Restart and hold right. Rocks travel left across the water. Hold left: they travel right. Release the key: they stop.
