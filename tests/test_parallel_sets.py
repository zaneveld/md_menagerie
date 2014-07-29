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
from md_menagerie.mapping import MappingTable
from md_menagerie.parallel_sets import get_top_level_sets_from_mapping


class ParallelSetsTests(TestCase):
    """Tests of the plots module."""
    def setUp(self):
        """Create some data to be used in the tests."""
        self.ParallelSetsTableLines =\
        ["#SampleID\tTemp\tTissueLoss\tAlgalContact\tDescription\n",\
         "#Comment line, full of crazy comments\n",\
         "#Another comment line\n",\
         "S.1\t21.0\tLoss\tYes\tSample.1.Description\n",\
         "S.2\t22.0\tLoss\tYes\tSample.2.Description\n",\
         "S.3\t23.0\tLoss\tNo\tSample.3.Description\n",\
         "S.4\t20.0\tNo_Loss\tNo\tSample.4.Description\n",\
         "S.5\t21.0\tLoss\tYes\tSample.5.Description\n",\
         "S.5b\t21.0\tNo_Loss\tNo\tSample.5.Description\n",\
         "S.6\t21.5\tNo_Loss\tNo\tSample.6.Description\n",\
         "S.7\t22.72\tLoss\tNo\tSample.7.Description\n",\
         "S.8\t23.14\tLoss\tYes\tSample.7.Description\n"]

        self.ParallelSetsTable =\
          MappingTable(self.ParallelSetsTableLines)

    def test_get_top_level_sets_from_mapping_OK_valid_input(self):
        """get_top_level_sets_from_mapping OK with valid input"""
        #parallel_sets form mapping should contruct
        #a dict of sets of samples, corresponding to different
        #subdivisions of the data.
        
        #Most Simple possible case is a single category
        categories = ['TissueLoss']
        exp = {\
                'TissueLoss':{'Loss':set(['S.1','S.2','S.3',\
        'S.5','S.7','S.8']),\
                'No_Loss':set(['S.4','S.5b','S.6'])}}
        
        mapping_table = self.ParallelSetsTable
        obs = get_top_level_sets_from_mapping(mapping_table,categories)
        self.assertEqualItems(obs,exp)

        #Try the same with two categoires
        categories = ['TissueLoss','Temp']
        exp = {
                'TissueLoss':{
                    'Loss':set(['S.1','S.2','S.3','S.5','S.7','S.8']),
                    'No_Loss':set(['S.4','S.5b','S.6'])
                },
                'Temp':{
                    '20.0':set(['S.4']),
                    '21.0':set(['S.1','S.5','S.5b','S.6']),
                    '22.0':set(['S.2']),
                    '21.5':set(['S.6']),
                    '22.72':set(['S.7']),
                    '23.0':set(['S.3']),
                    '23.14':set(['S.8'])
                }
        }
        
        mapping_table = self.ParallelSetsTable
        obs = get_top_level_sets_from_mapping(mapping_table,categories)
        self.assertEqualItems(obs,exp)



if __name__ == '__main__':
    main()
