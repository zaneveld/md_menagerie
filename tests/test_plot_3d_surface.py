#!/usr/bin/env python

"""Tests public and private functions in the plots module."""

from cogent.util.unit_test import TestCase, main
from plot_3d_surface import interpolate_y_on_x 

class PlotsTests(TestCase):
    """Tests of the plots module."""
    def setUp(self):
        """Create some data to be used in the tests."""
        # Test null data list.
        self.Null = None

        # Test empty data list.
        self.Empty = []

        # Test nested empty data list.
        self.EmptyNested = [[]]

        # Test nested empty data list (for bar/scatter plots).
        self.EmptyDeeplyNested = [[[]]]
        


        self.full_x = ["1.0","2.0","1.0","4.0","5.0","5.0","1.0"]
    
    def test_interpolate_y_on_x_works_without_missing_data(self):
        """test_interpolate_y_on_x should estimate missing values with valid data"""
        
        full_x = self.full_x
        full_y = [str(2*float(x)+0.1) for x in full_x]
        full_z = range(len(full_x)) 
        x,y,z = interpolate_y_on_x(full_x,full_y,full_z)
        exp_x = [1.0,1.0,1.0,2.0,4.0,5.0,5.0]
        exp_y = [2.1,2.1,2.1,4.1,8.1,10.1,10.1]
        exp_z = [6.0,0.0,2.0,1.0,3.0,4.0,5.0]
        self.assertEqualItems(exp_x,x)
        self.assertEqualItems(exp_y,y)
        self.assertEqualItems(exp_z,z)

    def test_interpolate_y_on_x_works_without_one_missing_value(self):
        """test_interpolate_y_on_x should estimate missing values with valid data"""
        
        full_x = self.full_x
        full_y = [str(2*float(x)+0.1) for x in full_x]
        full_y[3]="Unknown"
        full_z = range(len(full_x)) 
        x,y,z = interpolate_y_on_x(full_x,full_y,full_z)
        exp_x = [1.0,1.0,1.0,2.0,4.0,5.0,5.0]
        exp_y = [2.1,2.1,2.1,4.1,8.1,10.1,10.1]
        exp_z = [6.0,0.0,2.0,1.0,3.0,4.0,5.0]
        self.assertEqualItems(exp_x,x)
        self.assertEqualItems(exp_y,y)
        self.assertEqualItems(exp_z,z)
    
    def test_interpolate_y_on_x_works_with_missing_endpoint_data(self):
        """test_interpolate_y_on_x should estimate missing values with valid data"""
        full_x = self.full_x
        full_y = [str(2*float(x)+0.1) for x in full_x]
        full_z = range(len(full_x)) 
        partial_x = ["1.0","2.0","1.0","4.0","Unknown","5.0","1.0"]
        partial_y = ["Unknown","4.1","Unknown","8.1","10.1","Unknown","2.1"]
        exp_x = [1.0,1.0,1.0,2.0,4.0,5.0]
        exp_y = [2.1,2.1,2.1,4.1,8.1,8.1]
        exp_z = [6.0,0.0,2.0,1.0,3.0,5.0]
        x,y,z = interpolate_y_on_x(partial_x,partial_y,full_z)
        self.assertEqualItems(exp_x,x)
        self.assertEqualItems(exp_y,y)
        self.assertEqualItems(exp_z,z)
        

if __name__ == '__main__':
    main()
