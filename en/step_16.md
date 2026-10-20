## Start rocks at the top and bottom

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, add two more checks to `define appear`. Use `y` for the top and bottom edges.

```blocks3
if <key (up arrow v) pressed?> then
    set y to (160)
end
if <key (down arrow v) pressed?> then
    set y to (-160)
end
```

## Now run your code

Restart and hold up: rocks appear near the top. Restart and hold down: they appear near the bottom. Test one arrow key at a time.
