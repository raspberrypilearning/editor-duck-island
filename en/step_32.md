## Challenge: vary the rocks

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, add a second rock costume of a similar size. At the start of `define appear`, add:

```blocks3
switch costume to (pick random (1) to (2))
```

Leave the costumes on collectable and hazard alone.

## Now run your code

Restart and swim for a while. Both kinds of rock appear. Check that both still block the duck and disappear at the edges.
