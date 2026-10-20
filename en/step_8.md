## Make the wave bob

![wave.](images/wave-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **wave**, add a loop to move the ring down and up. These movements go the opposite way to the duck's gentle bob.

```blocks3
when green flag clicked
go to [back v] layer
switch costume to (costume1 v)
go to x: (0) y: (-20)
+forever
+    change y by (-1)
+    wait (0.3) seconds
+    change y by (1)
+    wait (0.3) seconds
+end
```

## Now run your code

Click the flag and leave the keys alone. The wave and duck bob in opposite directions.
