## Move rocks up and down

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, add these two checks below the sideways checks in `define move`.

```blocks3
if <key (up arrow v) pressed?> then
    change y by ((0) - (rock speed))
end
if <key (down arrow v) pressed?> then
    change y by (rock speed)
end
```

## Now run your code

Restart and hold up. Rocks move down. Hold down: they move up. Try all four arrows separately and check that the scenery always moves opposite the duck's direction.
