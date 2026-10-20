## Clear rocks at every edge

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **obstacle**, add a second check to `define disappear`. Check `y position` against `-160` and `160`.

```blocks3
define disappear
if <<((x position)) < (-220)> or <((x position)) > (220)>> then
    delete this clone
end
if <<((y position)) < (-160)> or <((y position)) > (160)>> then
    delete this clone
end
```

## Tip

These checks use position, not which key is held. They will also work for hazards that drift by themselves.

## Now run your code

Restart and swim up, down, left, and right. Rocks disappear after passing any boundary. Release the keys: rocks still inside the water stay where they are.
