import unittest
from check_casefold_paths import collisions


class CasefoldPathTests(unittest.TestCase):
    def test_case_only_pair(self):
        self.assertEqual(collisions(['a/DELTA.md', 'a/delta.md']), [('a/DELTA.md', 'a/delta.md')])

    def test_unicode_normalization(self):
        self.assertEqual(len(collisions(['cafe\u0301.md', 'caf\u00e9.md'])), 1)

    def test_different_directories_remain_distinct(self):
        self.assertEqual(collisions(['A/file.md', 'B/file.md']), [])

    def test_repeated_identical_path_is_not_collision(self):
        self.assertEqual(collisions(['a.md', 'a.md']), [])


if __name__ == '__main__':
    unittest.main()
