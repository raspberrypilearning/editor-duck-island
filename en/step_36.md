## Challenge: draw a game-over sign

Paint a new sprite called **game over** with a clear “Game over” message.

Add these scripts. Create a new broadcast message called **game over** in the receiver's menu.

```blocks3
when green flag clicked
hide
```

```blocks3
when I receive (game over v)
go to x: (0) y: (0)
go to [front v] layer
show
```

## Tip

The sign is ready to receive a message. The next challenge connects the hook to it.

## Now run your code

Click the green flag: the sign hides. Click the `when I receive game over` stack directly in the code area: the sign appears in front of the game. Restart to hide it again.
