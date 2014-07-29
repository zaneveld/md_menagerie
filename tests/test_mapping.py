#!/usr/bin/env python

"""Tests public and private functions in the plots module."""

from cogent.util.unit_test import TestCase, main
from mapping import MappingTable,average_points_by_x
from numpy import array

class MappingTests(TestCase):
    """Tests of the mapping class  module."""
    
    
    def setUp(self):
        """Create some data to be used in the tests."""
        
        self.ExpDOBMappingLines=\
        self.ValidMappingFileLines=\
        ["#SampleID\tBarcodeSequence\tLinkerPrimerSequence\tTreatment\tDOB\tDescription\n",\
        "#Example mapping file for the QIIME analysis package. These 9 samples are from a study of the effects of\n",\
        "#exercise and diet on mouse cardiac physiology (Crawford, et al, PNAS, 2009).",\
        "PC.354\tAGCACGAGCCTA\tYATGCTGCCTCCCGTAGGAGT\tControl\t20061218\tControl_mouse__I.D._354",\
        "PC.355\tAACTCGTCGATG\tYATGCTGCCTCCCGTAGGAGT\tControl\t20060817\tControl_mouse__I.D._355",\
        "PC.356\tACAGACCACTCA\tYATGCTGCCTCCCGTAGGAGT\tControl\t20060305\tControl_mouse__I.D._356"]
        self.ValidTable=MappingTable(self.ValidMappingFileLines)
        
        self.InterpolationTableLines=\
        ["#SampleID\tTemp\tGrowthRate\tDescription\n",\
         "#Comment line, full of crazy comments\n",\
         "#Another comment line\n",\
         "S.1\t1.0\t3.0\tSample.1.Description\n",\
         "S.2\t2.0\t2.0\tSample.2.Description\n",\
         "S.3\t3.0\t0.0\tSample.3.Description\n",\
         "S.4\t0.0\tUnknown\tSample.4.Description\n",\
         "S.5\t1.0\tUnknown\tSample.5.Description\n",\
         "S.6\t1.5\tUnknown\tSample.6.Description\n",\
         "S.7\t2.72\tUnknown\tSample.7.Description\n",\
         "S.8\t3.14\tUnknown\tSample.7.Description\n"]

        self.InterpolationTable = MappingTable(self.InterpolationTableLines)
        
        self.InterpolationTableWithDuplicateLines =\
        ["#SampleID\tTemp\tGrowthRate\tDescription\n",\
         "#Comment line, full of crazy comments\n",\
         "#Another comment line\n",\
         "S.1\t1.0\t3.0\tSample.1.Description\n",\
         "S.2\t2.0\t2.0\tSample.2.Description\n",\
         "S.3\t3.0\t0.0\tSample.3.Description\n",\
         "S.4\t0.0\tUnknown\tSample.4.Description\n",\
         "S.5\t1.0\tUnknown\tSample.5.Description\n",\
         "S.5b\t1.0\tUnknown\tSample.5.Description\n",\
         "S.6\t1.5\tUnknown\tSample.6.Description\n",\
         "S.7\t2.72\tUnknown\tSample.7.Description\n",\
         "S.8\t3.14\tUnknown\tSample.7.Description\n"]

        self.InterpolationTableWithDuplicate =\
          MappingTable(self.InterpolationTableWithDuplicateLines)
    
    
    def test_load_mapping_creates_a_mapping_table_from_valid_lines(self): 
        """new_mapping_lines joins new_data to a mapping file"""
        lines=self.ValidMappingFileLines
        obs_table=MappingTable(lines)
        
        exp_header=['SampleID','BarcodeSequence','LinkerPrimerSequence','Treatment',\
          'DOB','Description']
        exp_data=[['PC.354', 'AGCACGAGCCTA', 'YATGCTGCCTCCCGTAGGAGT', 'Control', '20061218', 'Control_mouse__I.D._354'],['PC.355', 'AACTCGTCGATG', 'YATGCTGCCTCCCGTAGGAGT', 'Control', '20060817', 'Control_mouse__I.D._355'], ['PC.356', 'ACAGACCACTCA', 'YATGCTGCCTCCCGTAGGAGT', 'Control', '20060305', 'Control_mouse__I.D._356']]
        
        self.assertEqualItems(obs_table.HeaderFields, exp_header)
        self.assertEqual(obs_table.Data,exp_data)

    def test_iterRows_iterates_over_valid_rows(self):
        """MappingTable.iterRows iterates over rows"""
        exp_first_row = ('PC.354',["PC.354","AGCACGAGCCTA","YATGCTGCCTCCCGTAGGAGT","Control","20061218","Control_mouse__I.D._354"])
        obs_table = MappingTable(self.ValidMappingFileLines)
        self.assertEqual(obs_table.iterRows().next(),exp_first_row)
    
    def test_iterRows_iterates_over_specified_rows(self):
        """MappingTable.iterRows iterates over specified rows"""
        exp_first_row = ('PC.356',["PC.356","ACAGACCACTCA","YATGCTGCCTCCCGTAGGAGT","Control","20060305","Control_mouse__I.D._356"])
        obs_table = MappingTable(self.ValidMappingFileLines)
        self.assertEqual(obs_table.iterRows(row_names=['PC.356']).next(),exp_first_row)
        
    def test_iterRowData_iterates_over_valid_rows(self):
        """MappingTable.iterRowData iterates over row data"""
        exp_first_row = ["PC.354","AGCACGAGCCTA","YATGCTGCCTCCCGTAGGAGT","Control","20061218","Control_mouse__I.D._354"]
        obs_table = MappingTable(self.ValidMappingFileLines)
        self.assertEqual(obs_table.iterRowData().next(),exp_first_row)
   
    def test_iterRowData_iterates_over_specified_rows(self):
        """MappingTable.iterRowData iterates over specified rows"""
        exp_first_row = ["PC.356","ACAGACCACTCA","YATGCTGCCTCCCGTAGGAGT","Control","20060305","Control_mouse__I.D._356"]
        obs_table = MappingTable(self.ValidMappingFileLines)
        self.assertEqual(obs_table.iterRowData(row_names=['PC.356']).next(),exp_first_row)
     

    def test_iterCols_iterates_over_valid_cols(self):
        """MappingTable.iterCols iterates over cols"""
        obs_table = MappingTable(self.ValidMappingFileLines)
        obs_cols = [c for c in obs_table.iterCols()]
        exp_cols = [('SampleID', ['PC.354', 'PC.355', 'PC.356']), ('BarcodeSequence', ['AGCACGAGCCTA', 'AACTCGTCGATG', 'ACAGACCACTCA']), ('LinkerPrimerSequence', ['YATGCTGCCTCCCGTAGGAGT', 'YATGCTGCCTCCCGTAGGAGT', 'YATGCTGCCTCCCGTAGGAGT']), ('Treatment', ['Control', 'Control', 'Control']), ('DOB', ['20061218', '20060817', '20060305']), ('Description', ['Control_mouse__I.D._354', 'Control_mouse__I.D._355', 'Control_mouse__I.D._356'])]
        self.assertEqual(obs_cols,exp_cols)
    
    def test_iterCols_iterates_over_specified_rows_and_cols(self):
        """MappingTable.iterCols iterates over specified valid cols"""
        obs_table = MappingTable(self.ValidMappingFileLines)
        obs_cols = [c for c in obs_table.iterCols(col_names=['BarcodeSequence','DOB'],row_names=['PC.354','PC.356'])]
        exp_cols = [('BarcodeSequence', ['AGCACGAGCCTA', 'ACAGACCACTCA']),('DOB', ['20061218', '20060305'])]
        self.assertEqual(obs_cols,exp_cols)
    
    def test_mergedColsAsText_merges_columns(self):
        """MappingTable.mergedColsAsText outputs merged column text"""
        
        obs_table = MappingTable(self.ValidMappingFileLines)
        obs_merged_output = obs_table.mergedColsAsText(cols=['BarcodeSequence','DOB'])
        exp_merged_output = [\
        "BarcodeSequence_DOB\n",\
        "AGCACGAGCCTA_20061218\n",\
        "AACTCGTCGATG_20060817\n",\
        'ACAGACCACTCA_20060305\n']
        self.assertEqual([c for c in obs_merged_output],exp_merged_output)


    def test_iterColData_iterates_over_valid_cols(self):
        """MappingTable.iterColData iterates over column data"""
        obs_table = MappingTable(self.ValidMappingFileLines)
        obs_cols = [c for c in obs_table.iterColData()]
        exp_cols = [['PC.354', 'PC.355', 'PC.356'],['AGCACGAGCCTA', 'AACTCGTCGATG', 'ACAGACCACTCA'],['YATGCTGCCTCCCGTAGGAGT', 'YATGCTGCCTCCCGTAGGAGT', 'YATGCTGCCTCCCGTAGGAGT'],['Control', 'Control', 'Control'],['20061218', '20060817', '20060305'],['Control_mouse__I.D._354', 'Control_mouse__I.D._355', 'Control_mouse__I.D._356']]
        self.assertEqual(obs_cols,exp_cols)
    

    def test_iterNumericCols_gives_valid_numeric_cols_with_default_fn(self):
        """MappingTable.iterNumericCols gives valid numeric data only"""
        obs_table = self.ValidTable
        exp_vals = [20061218.0, 20060817.0, 20060305.0]
        obs_vals = obs_table.iterNumericCols(['DOB']).next()
        #should be only one value since we have only 1 column

        self.assertEqualItems(exp_vals,obs_vals)

    def test_iterNumericCols_gives_valid_numeric_cols_with_custom_fn(self):
        """MappingTable.iterNumericCols gives valid numeric data only"""
        obs_table = self.ValidTable
        conversion_fn = lambda x: int(float(x))
        #We expect a nested list because more than one value can be 
        #iterated at once
        exp_vals = [20061218, 20060817, 20060305]
        obs_vals = obs_table.iterNumericCols(['DOB'],conversion_fn).next()
        self.assertEqualItems(exp_vals,obs_vals)
    
    def test_iterNonNumericDataByRow_iterates_nonnumeric_cols_with_valid_data(self):
        """MappingTable.iterNumericCols gives valid numeric data only"""
        obs_table = self.InterpolationTable
        conversion_fn = lambda x: int(float(x))
        obs=[val for val in obs_table.iterNonNumericDataByRow(col_names=['Temp','GrowthRate'],\
                conversion_fn=conversion_fn)]
        
        exp =[
          [0,'Unknown'],
          [1,'Unknown'],
          [1,'Unknown'],
          [2,'Unknown'],
          [3,'Unknown']]
        self.assertEqualItems(obs,exp)
 
    def test_splitByCol_functions_with_valid_textual_data(self):
        """MappingTable.splitTableByColumns generates a dict of new tables"""
        start_table = self.InterpolationTable
        new_tables = start_table.splitByCol(['Temp'])
        exp_keys = [('0.0',),('1.0',),('1.5',),('2.0',),('3.0',),('2.72',),('3.14',)]
        self.assertEqualItems(new_tables.keys(),exp_keys)
        
        #We expect the 1.0 entry to have all rows where
        #temperature == 1.0, plus all header and comment
        #rows

        exp_entry_1 =\
           ["#SampleID\tTemp\tGrowthRate\tDescription\n",\
           "#Comment line, full of crazy comments\n",\
           "#Another comment line\n",\
           "S.1\t1.0\t3.0\tSample.1.Description\n",\
           "S.5\t1.0\tUnknown\tSample.5.Description\n"]

        obs_entry_1 = new_tables[('1.0',)].delimitedSelf()
        self.assertEqualItems(obs_entry_1,exp_entry_1)

        #Check that the middle entries are split well 
        #also
        exp_entry_272 =\
           ["#SampleID\tTemp\tGrowthRate\tDescription\n",\
           "#Comment line, full of crazy comments\n",\
           "#Another comment line\n",\
           "S.7\t2.72\tUnknown\tSample.7.Description\n"]
        
        obs_entry_272 = new_tables[('2.72',)].delimitedSelf()
        self.assertEqualItems(obs_entry_272,exp_entry_272)
       
    def test_interpolate_gives_correct_output_with_valid_data(self):
        """MappingTable.interpolate correctly interpolates a short data series"""
        table = self.InterpolationTable
        # Test values taken from the scipy documentation here:
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html
        obs_x,obs_y = table.interpolate("Temp","GrowthRate")
        exp_y = array([3.0,3.0,2.5,0.56,0.0])
        self.assertFloatEqual(obs_y,exp_y)

    def test_interpolate_gives_correct_output_with_duplicate_data(self):
        """MappingTable.interpolate correctly interpolates a short data series,removing one y for duplicated x"""
        table = self.InterpolationTableWithDuplicate
        # Test values taken from the scipy documentation here:
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html
        obs_x,obs_y = table.interpolate("Temp","GrowthRate")
        exp_y = array([3.0,3.0,3.0,2.5,0.56,0.0])
        self.assertFloatEqual(obs_y,exp_y)

    def selectRowsByValue_returns_unique_rows_matching_val(self):
        """MappingTable.selectRowsByValue finds row_ids by column values"""
        table = self.InterpolationTableWithDuplicate
        #If only one unique
        obs = table.selectRowsByValue(1.0,'Temp',conversion_fn=float())
        #these are exactly 1.0
        exp = ['S.1','S.5']
        self.assertEqualItems(obs,exp)

    def selectRowsByValue_returns_closest_rows_below_val(self):
        """MappingTable.selectRowsByValue finds row_ids below column values"""
        table = self.InterpolationTableWithDuplicate
        #If only one unique
        obs = table.selectRowsByValue(1.0,'Temp',conversion_fn=float(),\
          sides='less_than')
        #should find the closest row with a lower temp value
        exp = ['S.4']
        self.assertEqualItems(obs,exp)

    def selectRowsByValue_returns_closest_rows_above_val(self):
        """MappingTable.selectRowsByValue finds row_ids above column values"""
        table = self.InterpolationTableWithDuplicate
        #If only one unique
        obs = table.selectRowsByValue(1.0,'Temp',conversion_fn=float(),\
          sides='greater_than')
        #should find the closest row with a higher temp value
        # Here, 1.5 is the next highest temp value
        exp = ['S.6']
        self.assertEqualItems(obs,exp)

    def test_updateCol_functions_with_valid_data(self):
        """MappingTable.updateCol should update a column"""
        table = self.InterpolationTableWithDuplicate
        obs = table.updateCol('GrowthRate','SampleID',{'S.5b':3.01,'S.5':2.59}).delimitedSelf()
        
        exp =\
        ["#SampleID\tTemp\tGrowthRate\tDescription\n",\
         "#Comment line, full of crazy comments\n",\
         "#Another comment line\n",\
         "S.1\t1.0\t3.0\tSample.1.Description\n",\
         "S.2\t2.0\t2.0\tSample.2.Description\n",\
         "S.3\t3.0\t0.0\tSample.3.Description\n",\
         "S.4\t0.0\tUnknown\tSample.4.Description\n",\
         "S.5\t1.0\t2.59\tSample.5.Description\n",\
         "S.5b\t1.0\t3.01\tSample.5.Description\n",\
         "S.6\t1.5\tUnknown\tSample.6.Description\n",\
         "S.7\t2.72\tUnknown\tSample.7.Description\n",\
         "S.8\t3.14\tUnknown\tSample.7.Description\n"] 
        self.assertEqualItems(obs,exp)

    def test_updateColByInterpolation(self):
        """MappingTable.updateColByInterpolation functions with valid data"""
        table = self.InterpolationTableWithDuplicate
        obs = table.updateColByInterpolation('GrowthRate','Temp').delimitedSelf()
        exp =\
        ["#SampleID\tTemp\tGrowthRate\tDescription\n",\
         "#Comment line, full of crazy comments\n",\
         "#Another comment line\n",\
         "S.1\t1.0\t3.0\tSample.1.Description\n",\
         "S.2\t2.0\t2.0\tSample.2.Description\n",\
         "S.3\t3.0\t0.0\tSample.3.Description\n",\
         "S.4\t0.0\t3.0\tSample.4.Description\n",\
         "S.5\t1.0\t3.0\tSample.5.Description\n",\
         "S.5b\t1.0\t3.0\tSample.5.Description\n",\
         "S.6\t1.5\t2.5\tSample.6.Description\n",\
         "S.7\t2.72\t0.56\tSample.7.Description\n",\
         "S.8\t3.14\t0.0\tSample.7.Description\n"] 
        self.assertEqualItems(obs,exp)
    
    def test_rowMatches(self):
        """MappingTable.rowMatches returns True for matching rows"""
        obs_table = self.ValidTable
        criteria={'SampleID':'PC.354'}
        obs = [obs_table.rowMatches(r,criteria) for r in obs_table.iterRowData()]
        exp = [True,False,False]
        self.assertEqual(obs,exp)


    def test_rowsMatching(self):
        """MappingTable.rowsMatching"""
        
        table = self.InterpolationTable
        obs = table.rowsMatching({'Temp':'1.0'})
        exp =\
        [("S.1",["S.1","1.0","3.0","Sample.1.Description"]),\
         ("S.5",["S.5","1.0","Unknown","Sample.5.Description"])]
        
        self.assertEqualItems(obs,exp)

    

class MappingFunctionTests(TestCase):
    """Tests for external functions in the mapping module"""

    def test_average_points_by_x_functions_with_list_data(self):
        """average_points_by_x_functions_with_valid_list_data"""
        x = [0,3,1,0,1]
        y = [7,0,2,5,3]
        exp_x = array([0,1,3])
        exp_y = array([6,2.5,0])
        obs_x,obs_y = average_points_by_x(x,y)
        self.assertFloatEqual(obs_x,exp_x)
        self.assertFloatEqual(obs_y,exp_y)

    def test_average_points_by_x_functions_with_array_data(self):
        """average_points_by_x_functions_with_valid_array_data"""
        x = array([0,3,1,0,1])
        y = array([7,0,2,5,3])
        exp_x = array([0,1,3])
        exp_y = array([6,2.5,0])
        obs_x,obs_y = average_points_by_x(x,y)
        self.assertFloatEqual(obs_x,exp_x)
        self.assertFloatEqual(obs_y,exp_y)

if __name__ == '__main__':
    main()
