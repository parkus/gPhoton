from __future__ import absolute_import, division, print_function
# Core and Third Party imports.
import numpy as np
import pandas as pd
import unittest

class TestArguments(unittest.TestCase):
    def setUp(self):
        self.bands = ['NUV','FUV']
        self.standard = {'NUV':pd.read_csv('DB10_calrun_NUV.csv'),
                         'FUV':pd.read_csv('DB10_calrun_FUV.csv')}
        self.testrun = {'NUV':pd.read_csv('DB10_calrun_NUV_test.csv'),
                        'FUV':pd.read_csv('DB10_calrun_FUV_test.csv')}

    # BEGIN TESTING DEFAULTS
    def test_everything(self):
        """Check the values of everything."""
        for band in ['NUV','FUV']:
            for k in list(self.standard[band].keys()):
                self.assertTrue(k in list(self.testrun[band].keys()))
                for i,val in enumerate(self.standard[band][k]):
                    if (np.isnan(self.standard[band][k][i]) and
                                        np.isnan(self.testrun[band][k][i])):
                        continue
                    self.assertAlmostEqual(self.standard[band][k][i],
                                            self.testrun[band][k][i],places=4)

suite = unittest.TestLoader().loadTestsFromTestCase(TestArguments)
unittest.TextTestRunner(verbosity=2).run(suite)
