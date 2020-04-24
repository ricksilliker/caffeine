import unittest
import shutil
import tempfile

from caffeine import actions


class TestActions(unittest.TestCase):
    def _createActionDirectory(self):
        self._tempActionDirectory = tempfile.mkdtemp(suffix='.action')

    def setUp(self):
        from maya import cmds

        cmds.file(new=True, force=True)
        self._tempActionDirectory = None

    def tearDown(self):
        if self._tempActionDirectory is not None:
            shutil.rmtree(self._tempActionDirectory)

    def test_loadDefaultActionsValid(self):
        defaultActions = actions.loadDefault()
        self.assertGreater(len(defaultActions), 0)

    def test_loadEmptyActionInvalid(self):
        self._createActionDirectory()
        action, err = actions.loadActionFromPath(self._tempActionDirectory)
        self.assertIsNotNone(err)


if __name__ == '__main__':
    unittest.main()
