## Animate the swimming wave

![wave.](images/wave-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **wave**, use the same four-arrow condition as the duck. While an arrow is held, change costume. Otherwise, return to the smallest ring and bob gently.

```blocks3
when green flag clicked
go to [back v] layer
switch costume to (costume1 v)
go to x: (0) y: (-20)
forever
+    if <<<key (right arrow v) pressed?> or <key (left arrow v) pressed?>> or <<key (up arrow v) pressed?> or <key (down arrow v) pressed?>>> then
        next costume
        wait (0.1) seconds
    else
        switch costume to (costume1 v)
        change y by (-1)
        wait (0.3) seconds
        change y by (1)
        wait (0.3) seconds
    end
end
```

## Now run your code

Click the flag. Hold an arrow: the ring expands repeatedly. Release it: the smallest ring returns and gently bobs. Space should not animate the ring.
