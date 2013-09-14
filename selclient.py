#!/usr/bin/env python2
#
# feivel jellyfish wrote this in 2013. do what you want.
#
# selclient.py is a trivial script that waits for changes to the PRIMARY
# X selection, and restores the last value if the selection has been cleared
# (e.g., when the last application to claim it exits). this lets you use
# clop.py to set its contents in the same way as the CLIPBOARD selection.

import clop
import gtk
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-daemon', dest='daemonize', action='store_false', default=True)
parser.add_argument('-s', '--selection', default='PRIMARY')
parser.add_argument('--debug', action='store_true', default=False)

class Clipboard(clop.Clipboard):
  def on_change(self, callback):
    self.__backend.connect('owner-change', callback)

class SelectionClient():
  def __init__(self, selection, debug=False):
    self.clipboard = Clipboard(selection)
    self.debug = debug

  def callback(self, cb, change):
    if self.debug:
      print("event: %s" % change)
      print("text:  %s" % self.clipboard.read())

    if change.reason is 0: # 0: new owner; 1: owner destroyed; 2: owner closed
      self.last = self.clipboard.read()
    else:
      self.clipboard.write(self.last)

  def start(self):
    self.last = self.clipboard.read() or ''
    self.clipboard.on_change(self.callback)
    gtk.main()


def daemonize():
  import os
  os.fork() and exit()
  os.setsid()
  os.fork() and exit()

  for fd in range(3):
    os.close(fd)

  for mode in 'rww':
    open(os.devnull, mode)

def main():
  opts = parser.parse_args()
  if opts.daemonize: daemonize()
  SelectionClient(opts.selection, opts.debug).start()

if __name__ == '__main__':
  main()

