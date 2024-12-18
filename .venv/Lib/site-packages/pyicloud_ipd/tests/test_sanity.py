from unittest import TestCase

from pyicloud_ipd.cmdline import main


class SanityTestCase(TestCase):
    def test_basic_sanity(self):
        with self.assertRaises(SystemExit):
            main(['--help'])
