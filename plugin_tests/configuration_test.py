from tests import base


def setUpModule():
    base.enabledPlugins.append('configuration')
    base.startServer()


def tearDownModule():
    base.stopServer()


class ColormapsTestCase(base.TestCase):
    def testPlaceholder(self):
        self.assertTrue(True)
