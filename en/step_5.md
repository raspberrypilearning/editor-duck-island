## Bob faster when swimming

![player.](images/player-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **player**, put the faster movement in an `if then else` block. Keep the gentle movement in `else`.

Join four `key pressed?` blocks using three `or` blocks. Check **only the arrow keys**.

```blocks3
when green flag clicked
forever
+    if <<<key (right arrow v) pressed?> or <key (left arrow v) pressed?>> or <<key (up arrow v) pressed?> or <key (down arrow v) pressed?>>> then
+        change y by (3)
+        wait (0.1) seconds
+        change y by (-3)
+        wait (0.1) seconds
+    else
+        change y by (1)
+        wait (0.3) seconds
+        change y by (-1)
+        wait (0.3) seconds
+    end
end
```

## Now run your code

Hold an arrow key: the duck bobs faster. Release it: the gentle bob returns. Press space: the gentle bob should continue.
