#!/usr/bin/env python2
#
# feivel jellyfish wrote this in 2013. do what you want.
#
# selclient.py is a trivial script that waits for changes to the PRIMARY
# X selection, and restores the last value if the selection has been cleared
# (e.g., when the last application to claim it exits). this lets you use
# clop.py to set its contents in the same way as the CLIPBOARD selection.

import clop
import argparse
import gtk

parser = argparse.ArgumentParser()
parser.add_argument('--no-fork', dest='fork', action='store_false', default=True)
parser.add_argument('-s', '--selection', default='PRIMARY')
parser.add_argument('--debug', action='store_true', default=False)

class Clipboard(clop.Clipboard):
  def on_change(self, callback):
    self.__backend.connect('owner-change', callback)

  def owner(self):
    return self.__backend.get_owner()

class SelectionClient():

  def __init__(self, selection, debug=False):
    self.clipboard = Clipboard(selection)
    self.debug = debug

  def callback(self, cb, change):

    txt = self.clipboard.read()
    if self.debug:
      print("event: %s" % change)
      print("text:  %s" % txt)
    if txt:
      self.last = txt
    if change.reason != 0: # 0: new owner; 1: owner destroyed; 2: owner closed
      self.clipboard.write(self.last)

  def start(self):
    self.last = self.clipboard.read() or ''
    self.clipboard.on_change(self.callback)
    gtk.main()

def main():
  import os
  opts = parser.parse_args()
  selclient = SelectionClient(opts.selection, opts.debug)
  if opts.fork:
    pid = os.fork()
    if pid == 0:
      selclient.start()
    else:
      print pid
  else:
    selclient.start()

if __name__ == '__main__':
  main()

