## Turn in every direction

![player.](images/player-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **player**, duplicate the right-arrow `if` block three times inside the same loop. Match each key to its costume.

```blocks3
forever
    if <key (right arrow v) pressed?> then
        switch costume to (right v)
    end
+    if <key (left arrow v) pressed?> then
        switch costume to (left v)
    end
+    if <key (down arrow v) pressed?> then
        switch costume to (down v)
    end
+    if <key (up arrow v) pressed?> then
        switch costume to (up v)
    end
end
```

## Now run your code

Press each arrow key separately. The duck faces right, left, down, and up when you press the matching key.
