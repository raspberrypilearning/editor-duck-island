## Hear each rescue

![collectable.](images/colletable-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **collectable**, open **Sounds**. The painted sprite you duplicated should include **pop**. If it is missing, choose **Pop** from the sound library.

Return to **Code** and add `start sound pop` before deleting a rescued clone.

```blocks3
if <touching (player v)?> then
    change [score v] by (1)
    start sound (pop v)
    delete this clone
end
```

## Tip

Use `start sound` so the clone can disappear immediately.

## Now run your code

Rescue a small duck. You hear a pop as it disappears, and the score still increases by one.
