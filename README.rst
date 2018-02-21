lung protagorista
=================
:version:1.0.3
:author:Gabriel Montagné Láscaris-Comneno gabriel@tibas.london

very bespoke drill tool.
el motor de toda esta picha.

install
------------

to install::

    python3 setup.py install

usage
-----------

to use::

    lung --help
     
    usage: lung [-h] [-s] [-f F [F ...]] [-l L [L ...]] [-cc CC [CC ...]]
                [-m M [M ...]] [-c [C]] [-qs [QS]] [-g G [G ...]] [-lw] [-cmd]

    optional arguments:
      -h, --help       show this help message and exit
      -s               sequential (non random)
      -f F [F ...]     files
      -l L [L ...]     lists
      -cc CC [CC ...]  flat, per comments
      -m M [M ...]     modules
      -c [C]           correct retries
      -qs [QS]         cuestion count
      -g G [G ...]     question grep
      -lw              lock weight
      -cmd             interactive CMD



sintaxis
-------------

to run a command::

  ex: xmessage "ok"


to assign an arbitrary initial weight to a question, start it with

  ^[W:x] 

where x is a float (needs the .) of the original weight.
the default assigned is 1.0  so 2.0 will make the item twice as likely to show up.
