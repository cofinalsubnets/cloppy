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
import json
import argparse
import sys
import gtk

version     = '0.0.1'
description = 'Persistent registers for storing and retrieving X clipboard data.'
default_regfile = os.path.expanduser('~/.registers.json')

parser = argparse.ArgumentParser(description=description)
parser.add_argument('-g', '--get', action='append')
parser.add_argument('-p', '--put', action='append')
parser.add_argument('-e', '--echo', action='append')
parser.add_argument('-d', '--delete', action='append')
parser.add_argument('--primary', dest='selection', action='store_const', const='PRIMARY',
                    default='CLIPBOARD', help= "use PRIMARY X selection instead of CLIPBOARD")
parser.add_argument('-V', '--version', action='version', version=('%(prog)s version ' + version))
parser.add_argument('--regfile', metavar='FILE', default=default_regfile,
                    help='store registers here instead of ' + default_regfile)

def main():
  opts      = parser.parse_args()
  registers = read_registers(opts.regfile)
  clipboard = Clipboard(opts.selection)
  orig      = registers.copy()

  for action in get_actions(opts):
    action(registers, clipboard)

  if registers != orig:
    write_registers(registers, opts.regfile)

def get_actions(opts):
  for opname in ['get', 'put', 'echo', 'delete']:
    for reg in (getattr(opts, opname) or []):
      yield lambda regs, cb: globals()[opname](regs, reg, cb)

def read_registers(regfile):
  """Attempt to read registers from disk."""
  if os.path.exists(regfile):
    with open(regfile, 'r') as rf:
      obj = json.load(rf)
    if not isinstance(obj, dict):
      raise TypeError("%s is not a dict" % obj)
    return obj
  return {}

def write_registers(registers, regfile):
  """Dump registers to disk."""
  with open(regfile, 'w') as rf:
    json.dump(registers, rf)

def get(registers, reg, clipboard):
  """Set clipboard contents from a register."""
  txt = registers.get(reg, '')
  clipboard.write(txt)

def put(registers, reg, clipboard):
  """Store clipboard contents in a register."""
  txt = clipboard.read()
  if isinstance(txt, str):
    registers[reg] = txt

def echo(registers, reg, clipboard):
  """Echo the contents of a register to stdout."""
  txt = registers.get(reg, '')
  sys.stdout.write(txt)

def delete(registers, reg, clipboard):
  """Delete a register."""
  if reg in registers:
    registers.pop(reg)

class Clipboard():
  """Wrapper for a clipboard implementation (currently GTK).
  Provides a uniform interface & enforces synchronous semantics."""
  def __init__(self, sel):
    self.__backend = gtk.clipboard_get(sel)
  def read(self):
    return self.__backend.wait_for_text()
  def write(self, txt):
    import time
    self.__backend.set_text(txt)
    self.__backend.store()
    time.sleep(0.05) # give other clients time to register the owner change
    while gtk.events_pending():
      gtk.main_iteration()



if __name__ == '__main__':
  main()

