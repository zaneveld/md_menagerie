#!/usr/bin/env python
# File created on 15 Jul 2011
from __future__ import division

__author__ = "Jesse Zaneveld"
__copyright__ = "Copyright 2014, The MetadataMenagerie Project"
__credits__ = ["Jesse RR Zaneveld"]
__license__ = "GPL"
__version__ = "0.1dev"
__maintainer__ = "Jesse Zaneveld"
__email__ = "zaneveld@gmail.com"
__status__ = "Development"

"""Tests the parallel_sets library functions."""

from cogent.util.unit_test import TestCase, main
from md_menagerie.parallel_sets import calc_parallel_set 
from md_menagerie.parallel_sets import parallel_sets_from_mapping


class ParallelSetsTests(TestCase):
    """Tests of the plots module."""
    def setUp(self):
        """Create some data to be used in the tests."""
        pass

    def test_parallel_sets_from_mapping(self):
        """test construction of parallel sets from mapping file"""
        pass

if __name__ == '__main__':
    main()
