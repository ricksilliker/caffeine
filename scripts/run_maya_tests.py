import os
import sys
import logging
import unittest

logging.basicConfig(level=logging.DEBUG)

LOG = logging.getLogger()
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(PROJECT_DIR, 'src')
TEST_DIR = os.path.join(PROJECT_DIR, 'tests')

def main():
    try: 			
        import maya.standalone
        maya.standalone.initialize()
        LOG.debug('Maya initialized.')
    except:
        LOG.exception('failed to initialize mayapy')
        return

    sys.path.append(SRC_DIR)
    LOG.debug('Appended project directories.')

    suite = unittest.TestSuite()
    LOG.debug('Loading tests from: %s', TEST_DIR)
    suite.addTests(unittest.defaultTestLoader.discover(start_dir=TEST_DIR))
    LOG.debug('Starting testing...')
    unittest.TextTestRunner().run(suite)


main()