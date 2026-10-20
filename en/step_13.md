## Vary the rock sizes

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, add a random size to `define appear`, before `show`.

```blocks3
define appear
go to x: (pick random (-200) to (200)) y: (pick random (-140) to (140))
+set size to (pick random (50) to (100)) %
show
```

## Now run your code

Restart several times. The rock changes size as well as position. It should stay between half and all of the size you drew.
