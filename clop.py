#!/usr/bin/env python2
#
# feivel jellyfish wrote this in 2013. do what you want.
#
# clop.py adds registers (like in vim or emacs) to the X window system.
# registers are stored on disk, so it doesn't need to run as a daemon.
# it's non-interactive and CLI-based so you can hook it up to your window
# manager or w/e.
#
# because of the way X selections work, clop.py can only usefully _set_
# the contents of selections with special-purpose X clients that will
# preserve their contents after exit. such a client normally only exists
# for the 'CLIPBOARD' selection, i.e. the one that's accessed when you do
# an explicit cut/paste. the 'PRIMARY' selection, which is normally
# updated when you highlight text and dumped with the middle mouse button,
# can't be changed with this tool alone (although you can read from it).
#
# if you want to use clop.py to set the contents of the PRIMARY selection,
# you can use it alongside the included selclient.py script, which _must_ run
# as a daemon to have any effect.

import os.path
import argparse
from sys import stdout
import gtk
from time import sleep
import re

version     = '0.0.1'
description = 'Persistent registers for storing and retrieving X clipboard data.'
default_regfile = os.path.expanduser('~/.registers')

operations = {
  'get'    : lambda r,rs,cb: cb.write(rs.get(r, '')),
  'put'    : lambda r,rs,cb: rs.__setitem__(r, escape(cb.read())),
  'echo'   : lambda r,rs,cb: stdout.write(rs.get(r, '')),
  'delete' : lambda r,rs,cb: rs.pop(r, None)
}

parser = argparse.ArgumentParser(description=description)
for op in operations:
  parser.add_argument('-' + op[0], '--' + op, action='append', default=[])
parser.add_argument('--primary', dest='selection', action='store_const', const='PRIMARY',
                    default='CLIPBOARD', help= "use PRIMARY X selection instead of CLIPBOARD")
parser.add_argument('-V', '--version', action='version', version=('%(prog)s version ' + version))
parser.add_argument('--regfile', metavar='FILE', default=default_regfile,
                    help='store registers here instead of ' + default_regfile)

def main():
  opts      = parser.parse_args()
  clipboard = Clipboard(opts.selection)
  registers = readin(opts.regfile)
  orig      = registers.copy()

  for op in operations:
    for reg in getattr(opts, op):
      operations[op](reg, registers, clipboard)

  if registers != orig:
    writeout(registers, opts.regfile)

def readin(regfile):
  """Attempt to read registers from disk."""
  if os.path.exists(regfile):
    with open(regfile, 'r') as rf:
      try:
        obj = load(rf)
      except Exception as err:
        raise ValueError("Corrupt registers file %s: %s" % (regfile, err))
    return obj
  return {}

def writeout(registers, regfile):
  """Dump registers to disk."""
  with open(regfile, 'w') as rf:
    dump(registers, rf)

class Clipboard():
  """Wrapper for a clipboard implementation (currently GTK).
  Provides a uniform interface & enforces synchronous semantics."""
  def __init__(self, sel):
    self.__backend = gtk.clipboard_get(sel)
  def read(self):
    """Return a string containing clipboard contents."""
    return self.__backend.wait_for_text() or ''
  def write(self, txt):
    """Set clipboard contents from a string."""
    self.__backend.set_text(txt)
    self.__backend.store()
    sleep(0.05) # give clients time to register the owner change
    while gtk.events_pending():
      gtk.main_iteration()


def escape(s, match_re=re.compile('([\\\\\n=])')):
  return match_re.sub('\\\\\g<1>', s)

def unescape(s, match_re=re.compile('\\\\(.|$)', re.MULTILINE)):
  return match_re.sub('\g<1>', s)

def loads(s, outer=re.compile('(?<!\\\\)\n', re.MULTILINE), inner=re.compile('(?<!\\\\)=')):
  return dict(map(lambda r: map(unescape, inner.split(r)), outer.split(s)))

def dumps(kvs):
  return '\n'.join(map(lambda kv: '='.join(map(escape, kv)), kvs.items()))

def load(readable):
  return loads(readable.read())

def dump(kvs, writeable):
  writeable.write(dumps(kvs))


if __name__ == '__main__':
  main()

