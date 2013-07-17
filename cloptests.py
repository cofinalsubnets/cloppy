#!/usr/bin/env python2
import unittest
import clop

class Mock():
  def __init__(self, **kwargs):
    for k in kwargs:
      setattr(self, k, kwargs[k])

class MockClipboard():
  def __init__(self, value=''):
    self.value = value
  def read(self):
    return self.value
  def write(self, txt):
    self.value = txt

class ClopTests(unittest.TestCase):
  def setUp(self):
    self.clipboard = MockClipboard()
    self.registers = {}

  def test_get(self):
    self.registers['a'] = 'b'
    clop.operations['get']('a', self.registers, self.clipboard)
    self.assertEqual('b', self.clipboard.value)
    self.assertEqual('b', self.registers['a'])

  def test_get_empty_register(self):
    self.clipboard.value = 'arbitrary'
    clop.operations['get']('a', self.registers, self.clipboard)
    self.assertEqual('', self.clipboard.value)
    self.assertNotIn('a', self.registers)

  def test_put(self):
    self.clipboard.value = 'peanuts'
    clop.operations['put']('squiggle', self.registers, self.clipboard)
    self.assertEqual(self.registers['squiggle'], 'peanuts')
    self.assertEqual(self.clipboard.value, 'peanuts')
  
  def test_put_full_register(self):
    self.registers['cockatoo'] = ('kliblop', 1.23124)
    self.clipboard.value = 'uggnog'
    clop.operations['put']('cockatoo', self.registers, self.clipboard)
    self.assertEqual(self.registers['cockatoo'], 'uggnog')
    self.assertEqual(self.clipboard.value, 'uggnog')

  def test_delete(self):
    self.registers['a'] = 'ohgodplease'
    clop.operations['delete']('a', self.registers, self.clipboard)
    self.assertNotIn('a', self.registers)

  def test_delete_empty_register(self):
    clop.operations['delete']('a', self.registers, self.clipboard)
    self.assertNotIn('a', self.registers)

  def test_readin_nonexistent_file(self):
    filename = 'zz:\\this\\is\\not\\a\\windows\\box'
    registers = clop.readin(filename)
    self.assertEqual(registers, {})

if __name__ == '__main__':
  unittest.main()

