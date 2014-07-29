#!/usr/bin/env python

"""Tests public and private functions in the plots module."""

from cogent.util.unit_test import TestCase, main
from add_metadata_to_mapping_file import parse_metadata
from summarize_contact_notes import calculate_event_stats,\
  make_two_level_defaultdict, parse_field_columns

class SummarizeContactDataTests(TestCase):
    """Tests of the summarize contact data module."""
    
    
    def setUp(self):
        """Create some data to be used in the tests."""
        # Test null data list.
        self.ValidMetadataFileLines =\
          ["#Season\tQualitativeTemp\tTempF\n",\
           "Summer\tHot\t95\n",\
           "Winter\tCold\t-10\n",\
           "Spring\tMild\t72\n",\
           "Autumn\tChilly\t50"]
        
        self.ValidDOBMetadataFileLines =\
          ["#DOB\tSeason\tQualitativeTemp\tTempF\n",\
           "20060817\tSummer\tHot\t95\n",\
           "20061218\tWinter\tCold\t-10\n",\
           "20060305\tSpring\tMild\t72\n",\
           "20061015\tAutumn\tChilly\t50"]
        
        self.ValidMappingFileLines=\
        ["#SampleID\tBarcodeSequence\tLinkerPrimerSequence\tTreatment\tDOB\tDescription\n",\
        "#Example mapping file for the QIIME analysis package. These 9 samples are from a study of the effects of\n",\
        "#exercise and diet on mouse cardiac physiology (Crawford, et al, PNAS, 2009).",\
        "PC.354\tAGCACGAGCCTA\tYATGCTGCCTCCCGTAGGAGT\tControl\t20061218\tControl_mouse__I.D._354",\
        "PC.355\tAACTCGTCGATG\tYATGCTGCCTCCCGTAGGAGT\tControl\t20060817\tControl_mouse__I.D._355",\
        "PC.356\tACAGACCACTCA\tYATGCTGCCTCCCGTAGGAGT\tControl\t20060305\tControl_mouse__I.D._356"]

        self.SimpleHeaderMap =\
          {"SampleId":0,"Treatment":1,"Disease":2,"ConcatenatedDate":3}

        self.SimpleCoralFields=[\
          ["1","Fertilizer_Yes_Caging_Yes", "Yes", "20090827"],\
          ["1","Fertilizer_Yes_Caging_Yes", "Yes", "20090905"],\
          ["2","Fertilizer_No_Caging_No", "No", "20090827"],\
          ["2","Fertilizer_No_Caging_No", "Yes", "20090905"],\
          ["2","Fertilizer_No_Caging_No", "No", "20090915"]]


    def test_calculate_event_stats(self):
        """Calculate_event_stats calculates statistics given valid inputs"""
        results = calculate_event_stats(self.SimpleCoralFields,self.SimpleHeaderMap,individual_column='SampleId',effect_column='Disease',\
          treatment_column='Treatment',time_column='ConcatenatedDate')
        print results
        #Results should be simple_effect_counts, individual_effect_counts, treatment 
        simple_counts,individuals_by_effect,counts_by_effect = results
        
    def test_parse_field_columns_processes_valid_input(self):
        """parse_field_columns processes valid input"""

        
        #Try with full specification of treatment and time
        metadata = parse_field_columns(self.SimpleCoralFields[0],self.SimpleHeaderMap,'SampleId','Disease',\
          'Treatment','ConcatenatedDate')
        
        
        self.assertEqual(metadata['Individual'],"1")
        self.assertEqual(metadata['Effect'],"Yes")
        self.assertEqual(metadata['Treatment'],"Fertilizer_Yes_Caging_Yes")
        self.assertEqual(metadata['Time'],20090827)

        #Try with no time or treatment data specified
        metadata = parse_field_columns(self.SimpleCoralFields[0],self.SimpleHeaderMap,'SampleId','Disease')
        self.assertEqual(metadata['Individual'],"1")
        self.assertEqual(metadata['Effect'],"Yes")
        self.assertTrue('Time' not in metadata.keys())
        self.assertTrue('Treatment' not in metadata.keys())

    def test_make_two_level_defaultdict_makes_two_level_integer_dict(self): 
        """make_two_level_defaultdict_int generates a two-level defaultdict from valid input"""
        new_defaultdict = make_two_level_defaultdict(dict_type = int)
        new_defaultdict[82]['BiteScars'] +=15
        new_defaultdict['2']['No'] +=45
        new_defaultdict['2']['No'] +=4
        # check that arbitrary labels are set to 0
        self.assertEqual(new_defaultdict['armadillo']['any_field'],0)
        # check that first input is preserved
        self.assertEqual(new_defaultdict[82]['BiteScars'],15)
        # check that second and third inputs are added properly
        self.assertEqual(new_defaultdict['2']['No'],49)



    
       
if __name__ == '__main__':
    main()
