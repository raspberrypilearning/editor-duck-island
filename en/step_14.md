## Make rocks while swimming

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, replace the single `create clone` with a loop. Make a clone only while an arrow key is held, then wait between `1` and `3` seconds.

```blocks3
when green flag clicked
hide
+forever
+    if <<<key (right arrow v) pressed?> or <key (left arrow v) pressed?>> or <<key (up arrow v) pressed?> or <key (down arrow v) pressed?>>> then
+        create clone of (myself v)
+        wait (pick random (1) to (3)) seconds
+    end
+end
```

## Tip

Restart to clear the rocks. They will move and disappear in later steps; keep these early tests short.

## Now run your code

Restart, then hold an arrow for a few seconds. Several rocks appear with gaps between them. Release the key: no new rocks should appear. Pressing space alone should not create rocks.
