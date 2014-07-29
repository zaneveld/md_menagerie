#!/usr/bin/env python
# File created on 15 Jul 2011
from __future__ import division
from warnings import warn

__author__ = "Jesse Zaneveld"
__copyright__ = "Copyright 2014, The MetadataMenagerie Project"
__credits__ = ["Jesse RR Zaneveld"]
__license__ = "GPL"
__version__ = "0.1dev"
__maintainer__ = "Jesse Zaneveld"
__email__ = "zaneveld@gmail.com"
__status__ = "Development"


from warnings import warn
from collections import defaultdict
from cogent.util.option_parsing import parse_command_line_parameters, make_option
from string import strip
from datetime import date
from md_menagerie.calc_time_interval import string_to_date 

script_info = {}
script_info['brief_description'] = "Given a mapping file with metadata specifying a start date, end date and sample date, generate a new metadata file with a treatment column modified according to whether samples fall before, during, or after treatment."
script_info['script_description'] =\
"""
"""

script_info['script_usage'] = [("","","")]
script_info['output_description']= "Output is metadata table (for use with add_metadata_to_mapping_file.py)"
script_info['required_options'] = [\
make_option('-i','--input_mapping_file',type="existing_filepath",\
  help='the input QIIME format mapping file '),\
  make_option('--start_time_column',\
  help='column that specifies the start time for the experiment in yyyymmdd format.'),\
  make_option('--sample_time_column',\
  help='column that specifies the sample time for that specific sample in yyyymmdd format.'),\
  make_option('--end_time_column',\
  help='column that specifies the sample time the experiment ended in yyyymmdd format.'),\
]
script_info['optional_options'] = [\
  make_option('-o','--output_mapping_file',type="new_filepath",\
   default=None,help='the output filepath for the new mappinging file, updated with metadata [default: based on input filename]'),\
  make_option('--pre_suffix',default='_pretreatment'
      help='suffix for pre-treatment samples [Default:%default]'),\
  make_option('--post_suffix',default='_posttreatment'
      help='suffix for pre-treatment samples [Default:%default]'),\
   ]
script_info['version'] = __version__


def mapping_line_to_metadata_dict(line,header_index_dict,field_delimiter="\t",line_delimiter="\n"):
    """Return a dict of metadata_key: metadata value for a given data line.  
    NOTE: in this dict SampleID is treated as a metadata value"""
    fields = line.strip(line_delimiter).split(field_delimiter)
    md = {fields[header_index_dict[k]] for k in header_index_dict.keys()}
    return md

def index_columns_by_header(header_line,field_delimiter="\t",line_delimiter="\n"):
    """Return a dict indexing columns by their order in the header
    Result will be a header_col:index dict"""

    headers = line.lstrip('#').strip(line_delimiter).split(field_delimiter)
    header_index_dict = {h:i for i,h in enumerate(headers)} 
    return header_index_dict

def new_metadata_by_per_sample_formula(lines,f,new_col_name='derived_metadata'):
    """Return a new metadata column based on the results of running f on metadata for this sample
    lines - lines of a QIIME mapping file
    f - a function taking a dict of header:value entries for this sample, and returning a single 
    string as output
    new_col_name - the name of the metadata column to be output
    vals_to_skip
    
    
    """
    
    yield "#SampleID\t%s\n" %new_col_name
    for i,line in enumerate(lines):
        if i==0 and line.startswith('#'):
            header_index_dict = index_columns_by_header
        elif line.startswith('#'):
            continue
        else:
            #We're in a data line
            metadata = mapping_line_to_metadata_dict(line,header_index_dict)
            sample_id = metadata['SampleID']
            new_col = f(metadata)
            yield "\t".join(sample_id,new_col)+"\n"
            
            
            
def make_HERBVREdate_span_function(start_date_header='start_date',sample_time_header='date',end_date_header='end_date',\
        suffix_output_dict={'=start':'treatment','=end':'post','<start':'pre','>end':'damaged'):
    """Make a function to modify treatments for project HERBVRE specifically"""
    

        sample_id = fields[header_index_dict['SampleID']]
        
        #Get relevant date strings for start, stop, sampling date
        current_date_str = metadata[curr_time_header]
        start_date_str = metadata[start_time_header]
        end_date_str = metadata[end_time_header]

        #Convert all to Date objects instead of strings
        current_date = string_to_date(current_concatenateddate)
        start_date = string_to_date(start_concatenateddate)
        end_date = string_to_date(end_concatenateddate)

        
        #Don't fail on "Unknown" date values
        #TODO: parameterize 'Unknown'`
        if current_concatenateddate in vals_to_skip or\
          start_concatenateddate in vals_to_skip:
            yield "\t".join([sample_id,"Unknown"])
            continue 

def main():
    option_parser, opts, args =\
       parse_command_line_parameters(**script_info)
  
    
    metadata_file_delimiter = ','
    mapping_file_delimiter = '\t'

    #Open output file
    print "Opening output file:",opts.output_mapping_file
    outfile = open(opts.output_mapping_file,'w+')

    
    #Load old QIIME mapping file.  Parse header line, then for each data line,
    #insert new fields just before description
    print "Loading input QIIME mapping file:",opts.input_mapping_file
    old_mapping_file = open(opts.input_mapping_file,'U')
    

    result = modify_metadata_by_date(old_mapping_file,opts.start_time_column,opts.curr_time_column) 


    
    #print "Result:", result
    for l in result:
        outfile.write(l)
        print l.strip()
    print "Done. Output saved to:",opts.output_mapping_file
    outfile.close()

if __name__ == "__main__":
    main()
