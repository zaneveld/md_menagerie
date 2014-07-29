
#!/usr/bin/env python
# File created on 15 Jul 2011
from __future__ import division
from warnings import warn

__author__ = "Jesse Zaneveld"
__copyright__ = "Copyright 2014, The HERBVRE Project"
__credits__ = ["Jesse RR Zaneveld"]
__license__ = "GPL"
__version__ = "0.1dev"
__maintainer__ = "Jesse Zaneveld"
__email__ = "zaneveld@gmail.com"
__status__ = "Development"


from warnings import warn
from collections import defaultdict
from copy import copy
from string import strip
try:
    from cogent.util.option_parsing import parse_command_line_parameters, make_option
except ImportError:
    raise ImportError("Could not import option parsing from cogent.util.option_parsing.  Is PyCogent installed (you can run this script within MacQIIME or the QIIME virtualbox to make use of a 'pre-packaged' PyCogent installation)")
from mapping import MappingTable

script_info = {}
script_info['brief_description'] = "Perform missing data interpolation on a QIIME mapping file."
script_info['script_description'] =\
"""
This script assists in interpolating missing data for QIIME mapping files.  This is used in cases where some column values are unknown, but are predictable from known column values.   For example, algal cover measurements may be generally stable on the course of weeks, but taken quarterly.  This script would allow interpolation of values for the weeks in which no measurement was taken.

"""

script_info['script_usage'] = [("","Generate a 3d plot of temperature x month x equitability for control samples found in the mapping file herbivore_mapping_r15_with_alpha.txt.  Save to output file 3d_plot_test.png",\
        "%prog -m ./test_script_data/herbivore_mapping_r15_with_alpha.txt -c 'HCOM_temp_5m,month,equitability_even_500_alpha' -f 'treatment:Control' -o ./test_script_data/3d_plot_test.png")]
script_info['output_description']= "Output is a new QIIME mapping file, with interpolated data values added."
script_info['required_options'] = [\
make_option('-m','--input_mapping_file',type="existing_filepath",\
  help='the input QIIME format mapping file.'),\
  make_option('-y','--interpolation_columns',\
  help='A comma-separated list of metadata headers to interpolate (i.e. the y axis in a linear regression)'),\
  make_option('-x','--reference_column',\
  help='A reference column over which to interpolate (i.e. the x axis in a linear regression'),\
]
script_info['optional_options'] = [\
 make_option('-s','--split_col',default=None,
    help="Name of columns to use in splitting up the dataset before interpolation (e.g. interpolate only within data that share values for all of these columns).  If provided, the table will be split based on all unique values of this column and results interpolated within each, then merged back into a single output [default:%default]"),\
 make_option('-o','--output_file',type="new_filepath",\
   default='interpolated_vals.txt',help='the output filepath for interpolated values.[default: %default]'),\
]

script_info['version'] = __version__

 

if __name__ == "__main__":
    option_parser, opts, args =\
      parse_command_line_parameters(**script_info)

    infile = open(opts.input_mapping_file,"U")
    outfile = open(opts.output_file,"w")
    
    input_mapping_table = MappingTable(infile.readlines())
    y_cols=opts.interpolation_columns.split(",")
    x_col=opts.reference_column
    
    
    if opts.split_col is None:
        mapping_tables = [input_mapping_table]
        mapping_table_labels = ['all_data']
    else:
        group_by_cols = opts.split_col.split(",")
        mapping_table_dict = input_mapping_table.splitByCol(group_by_cols)
        print "mapping_table_dict:",mapping_table_dict
        mapping_tables = []
        mapping_table_labels = []
        for m in mapping_table_dict.iteritems():
            print m
            mapping_tables.append(m[1])
            print len(m[1].Data)
            mapping_table_labels.append(m[0])

        
    #We want to generate a collection of tables, one for each value in
    # the split column.  This lets users e.g. interpolate pH vs. growth within
    # treatment categories.

    header_and_comments_written = False 
    for i,mapping_table in enumerate(mapping_tables):
        print "Interpolating table length:",len(mapping_table.Data) 
        if len(mapping_table.Data) < 5:
            #for line in mapping_table.delimitedSelf():
            #    print line
            print "Skipping table for %s (has only %i rows)" %(mapping_table_labels[i],len(mapping_table.Data))

        for y_col in y_cols:  
            mapping_table.updateColByInterpolation(y_col,x_col)
       
        #we want to merge tables in output
        #so only the first table will write its header and comments
        if not header_and_comments_written:
            for line in mapping_table.delimitedSelf():
                outfile.write(line)
            header_and_comments_written = True
            continue
        
        #skip comments on subsequent merged tables
        for line in mapping_table.delimitedSelf(write_header=False,\
          write_comments=False):
                outfile.write(line)
    
    outfile.close()
    
