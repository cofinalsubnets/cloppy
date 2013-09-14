clop.py
===
`clop.py` hacks registers (like in emacs or vim - basically named text buffers)
into the X windowing system's clipboard.

how to use
===
```shell
clop.py -p zebra      # put the current clipboard contents into the register `zebra'
clop.py -g gazelle    # retrieve the contents of `gazelle' and place on clipboard
clop.py -e antelope   # echo the contents of `antelope'
clop.py -d wildebeest # delete `wildebeest'
clop.py --primary -p giraffe # set the contents of `giraffe' from the PRIMARY X selection (see below)
```

idiot why would i want to set my clipboard contents on the command line
====
you probably wouldn't. just set up keybindings to run clop.py from your window
manager or w/e.

selclient.py
===
X's clipboard actually consists of things called selections. you can have
arbitrarily many, but most applications only use two: CLIPBOARD and PRIMARY.
the CLIPBOARD selection is the one that's used when you explicitly copy/paste
something; the PRIMARY selection is the one that's set when you highlight text,
and dumped when you press the middle mouse button.

a thing about selections is that they don't actually store text. an application
can tell X that it owns a certain selection; then that selection's contents
will be requested from the owner as needed. but if the owner exits, the
selection contents go with it.

the CLIPBOARD selection usually has a special-purpose client running that will
restore its contents in the even that the last application to claim it exits.
this is not the case for the PRIMARY selection, and hence you can't use clop.py
to set the PRIMARY selection's contents without running an analogous client.

`selclient.py` is a daemon that watches the PRIMARY selection, and restores its
contents any time its owner is closed or destroyed. it should allow you to set
the contents of the PRIMARY selection by running `clop.py ` with the --primary
flag. but it might not work 100% of the time if the application that claims
the PRIMARY selection exits very, very quickly. PRs welcome.

dependencies
===
`clop.py` currently depends on PyGTK, which is kind of silly.

