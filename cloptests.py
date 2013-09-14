#!/usr/bin/env python2
import unittest
import clop

class MockClipboard():
  def read(self):
    return self.__text
  def write(self, txt):
    self.__text = txt

class ClopTests(unittest.TestCase):
  def setUp(self):
    self.clipboard = MockClipboard()
    self.registers = {}

  def test_get(self):
    self.registers['a'] = 'b'
    clop.operations['get']('a', self.registers, self.clipboard)
    self.assertEqual('b', self.clipboard.read())
    self.assertEqual('b', self.registers['a'])

  def test_get_empty_register(self):
    self.clipboard.write('arbitrary')
    clop.operations['get']('a', self.registers, self.clipboard)
    self.assertEqual('', self.clipboard.read())
    self.assertNotIn('a', self.registers)

  def test_put(self):
    self.clipboard.write('peanuts')
    clop.operations['put']('squiggle', self.registers, self.clipboard)
    self.assertEqual(self.registers['squiggle'], 'peanuts')
    self.assertEqual(self.clipboard.read(), 'peanuts')
  
  def test_put_full_register(self):
    self.registers['cockatoo'] = ('kliblop', 1.23124)
    self.clipboard.write('uggnog')
    clop.operations['put']('cockatoo', self.registers, self.clipboard)
    self.assertEqual(self.registers['cockatoo'], 'uggnog')
    self.assertEqual(self.clipboard.read(), 'uggnog')

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

