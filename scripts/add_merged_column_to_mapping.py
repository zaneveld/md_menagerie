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


from warnings import warn
from collections import defaultdict
from copy import copy
try:
    from cogent.util.option_parsing import parse_command_line_parameters, make_option
except ImportError:
    raise ImportError("Could not import option parsing from cogent.util.option_parsing.  Is PyCogent installed (you can run this script within MacQIIME or the QIIME virtualbox to make use of a 'pre-packaged' PyCogent installation)")
from string import strip

script_info = {}
script_info['brief_description'] = "Given a mapping file and the tab-delimited file of metadata on organisms or genes, add metadata to the mapping file."
script_info['script_description'] =\
"""
"""

script_info['script_usage'] = [("","","")]
script_info['output_description']= "Output is a new QIIME mapping file, with metadata from one or more metadata files added."
script_info['required_options'] = [\
make_option('-i','--input_mapping_file',type="existing_filepath",\
  help='the input QIIME format mapping file.'),\
make_option('--mapping_columns_to_merge',\
  help='a comma-separated list of column names that will be generated.'),\
make_option('--merged_column_delimiter',default='_',\
  help='')
]
script_info['optional_options'] = [\
 make_option('--first_cols',default='SampleID,BarcodeSequence,LinkerPrimerSequence,#LinkerPrimerSequence',\
   help='a comma-delimited string describing columns to place at the start of the mapping file. If supplied, ensure that these columns are first in the output file [default: %default]'),\
 make_option('--last_cols',default='Description,DESCRIPTION',\
   help='if supplied, ensure that these columns are last in the output file [default: %default]'),\
 make_option('-o','--output_metadata_file',type="new_filepath",\
   default='./new_columns.txt',help='the output filepath for the new mapping file,  with updated metadata [default: based on input filename]')]
script_info['version'] = __version__




def supplement_mapping_file(old_mapping_file_lines,new_metadata_file_lines,\
    col_to_match,first_cols=[],last_cols=[],metadata_delimiter="\t",merged_col_delim="_"):
    """Supplement a mapping file with new entries from a metadata file

    """

    #handle special columns that with '&&' markers requesting
    #column merges in mapping file before matching
    if "&&" in col_to_match:
        cols_to_merge = col_to_match.split("&&")
        print "ADDING MERGED COLUMN:",cols_to_merge
        old_mapping_file_lines =\
             add_merged_column_to_mapping(old_mapping_file_lines,cols_to_merge,\
             merged_col_delim="_",delimiter="\t")
        #update col to match to be the merged column
        col_to_match=merged_col_delim.join(cols_to_merge)
        print "ADDED MERGED COLUMN:",col_to_match
    

    #Preparse new metadata file
    new_header_entries, new_metadata=\
      parse_metadata_lines(new_metadata_file_lines,col_to_match,\
      delimiter=metadata_delimiter)

    #Add new metadata to old mapping file
    result = new_mapping_lines(old_mapping_file_lines,new_metadata,new_header_entries,col_to_match,delimiter=metadata_delimiter,default_value='Unknown',default_method='default', first_fields=first_cols,last_fields=last_cols)
    return result

def parse_metadata_lines(metadata_lines,col_to_match,delimiter="\t"):
    """Get new mapping file entries given metadata lines
    metadata lines -- lines from the metadata file (to be added to the mapping file)
    """
    #New data will be keyed by the mapping_column value
    metadata= {}
    header_line = metadata_lines.next()
    header_fields = map(strip,header_line.strip('#').split(delimiter))
    for line in metadata_lines:
        metadata_fields = map(strip,line.split(delimiter))
        try:
            metadata_key_idx = header_fields.index(col_to_match)
        except ValueError:
            raise ValueError("col_to_match: %s not in header fields: %s" %(col_to_match,str(header_fields)))
        key = metadata_fields[metadata_key_idx]
        
        new_metadata_entries =\
          [d for i,d in enumerate(metadata_fields) if i != metadata_key_idx]
        
        new_header_entries =\
          [h for i,h in enumerate(header_fields) if i != metadata_key_idx] 
        
        #OLD: new_data used to contain lists of data entries
        #new_data[new_data_key] = new_data_entries
        
        metadata[key] = dict(zip(new_header_entries,new_metadata_entries))
    
    #Check for bad headers
    for header in new_header_entries:
        if len(header) == 1:
            raise ValueError("Bad header value (length 1):",header)
    
    #although the new data columns are also implicit in new_data
    #they are returned as a list to allow for preservation of ordering
    
    return new_header_entries, metadata    

def add_merged_column_to_mapping(mapping_file_lines,cols_to_merge,merged_col_delim="_",delimiter="\t"):
    """Add a new line to a mapping file, which merges each column in cols_to_merge
    mapping_file_lines:  iterator of lines for a QIIME mapping file
    cols_to_merge: list of columns to merge into a single new column
    merged_col_delim:  value used to join cols_to_merge
    delimiter: overall delimiter for fields
    """

    for i,line in enumerate(mapping_file_lines):
        line_type = identify_mapping_file_line_type(i,line)
        if line_type == 'blank':
            continue
        elif line_type == 'header':
            header_columns=map(strip,line.lstrip('#').split(delimiter))
            #col_indices_to_merge=\
            #  [i for i,col in enumerate(header_columns) if col in cols_to_merge]
            new_header_entries =\
               [merged_col_delim.join(cols_to_merge)]
            yield fields_to_line(header_columns+new_header_entries,delimiter=delimiter,comment_marker="#")
        elif line_type == 'comment':
            yield line #other comment line, keep it intact
        elif line_type == 'data':
            old_data_fields = map(strip,line.strip().split("\t"))
            #new_data =\
            #     merged_col_delim.join([d for i,d in enumerate(old_data_fields) if i in col_indices_to_merge])
            #BAD!!!! the above  reorders columns
            new_data = []
            for col in cols_to_merge:
                col_index = header_columns.index(col)
                new_data.append(old_data_fields[col_index])
            new_data = merged_col_delim.join(new_data)
            new_data_fields = old_data_fields
            new_data_fields.append(new_data)
            result = delimiter.join(new_data_fields)
            yield "%s\n" %result




def new_mapping_lines(old_mapping_lines,metadata,new_header_entries,col_to_match,\
  delimiter="\t",default_value='Unknown',\
  default_method='default', first_fields=['SampleID','BarcodeSequence',\
  'LinkerPrimerSequence'],last_fields=['Description']):
    """Yield new mapping file lines from the old QIIME mapping file + new metadata
    """

    for i,line in enumerate(old_mapping_lines):

        #Cleanup quotes and double-quotes
        line = line.strip('"').strip("'")
        line_type = identify_mapping_file_line_type(i,line)

        if line_type == 'blank':
            continue #skip blank lines

        elif line_type == 'header':
            
            mapping_columns=map(strip,line.lstrip('#').split(delimiter))
            output_header_entries = mapping_columns + new_header_entries
            #NOTE: the index column col_to_match will be in mapping_columns
            # but not new_header_entires
            output_header_entries = sort_fields(output_header_entries,\
              first_fields,last_fields)
            
            #First line will be the ordered, commented header
            yield  fields_to_line(output_header_entries,delimiter,\
              comment_marker="#")

        elif line_type == 'comment':
            #Uninteresting comment line, replicated
            #without modification
            yield line

        elif line_type == 'data':
           # print line 
            mapping_data_fields = map(strip,line.strip().split(delimiter))
            #print mapping_data_fields
            mapping_data = dict(zip(mapping_columns,mapping_data_fields))
            #print mapping_data
            #update the dictionary of data values
            try: 
                metadata_for_this_line =\
                    metadata.get(mapping_data[col_to_match],None)
            except KeyError:
                raise KeyError("Couldn't find col_to_match: %s in mapping data:%s" %(col_to_match,str(mapping_data.keys())))
            #print metadata_for_this_line

            if metadata_for_this_line is not None:
                metadata_for_this_line.update(mapping_data) 
                mapping_data = metadata_for_this_line
            #then write to the file linearly filling in missing vals as 
            #needed
            output_fields = []
            default = "Unknown"
            for entry in output_header_entries:
                #each entry is a column we must have
                #print "mapping_data:",mapping_data
                value=mapping_data.get(entry,default)
                output_fields.append(value) 
            yield fields_to_line(output_fields)


def update_data_by_exact_match(data,header_fields,new_data,new_header_fields,\
    mapping_col,default="Unknown"):

    mapping_line_data=dict(zip(header_fields,data))
    value_to_match = mapping_line_data[mapping_col]
    default_result = {h:default for h in new_header_fields}
    mapping_line_data.update(new_data.get(value_to_match,default_result))
    return mapping_line_data

    
    
def sort_fields(all_fields,first_fields,last_fields,unique_only=True):
    if unique_only:
        #Clunky approach, but not using Set in order to preserve
        #field order.
        unique_fields = []
        for f in all_fields:
            if f not in unique_fields:
                unique_fields.append(f)
        all_fields=unique_fields

    middle_fields =\
      [f for f in all_fields if f not in first_fields and f not in last_fields]
    
    first_fields =\
      [f for f in first_fields if f in all_fields]
    
    last_fields =\
      [f for f in last_fields if f in all_fields]
    
    ordered_fields = first_fields + middle_fields + last_fields
    return ordered_fields


def fields_to_line(fields,delimiter="\t",comment_marker=''):
    """Convert list of fields to output line"""
    return "%s%s\n" %(comment_marker,delimiter.join(fields))


def identify_mapping_file_line_type(i,line,required_first_field='#SampleID'):
    """return the line type as a string based on line number and line contents
    i -- the line number 
    line -- the line

    output -- type will be returned as a string: values are 'blank','header','comment' or 'data'
    """

    if not line.strip():
        return 'blank'
    elif i==0 and required_first_field is not None\
        and not line.startswith(required_first_field):
        print "BAD FIRST LINE:", line
        raise IOError("First line of mapping file must start with a '#SampleID' (check capitalization, no space between '#' and 'S').  Please makes sure mapping file is in valid QIIME format")

    elif i==0:
        return 'header'
    elif line.startswith('#'):
        return 'comment'
    else:
        return 'data'




def main():
    option_parser, opts, args =\
       parse_command_line_parameters(**script_info)
  
    if opts.input_mapping_file == opts.output_metadata_file:
        raise ValueError("Overwriting input not currently supported.  Input and output files must be different.")
    
    metadata_file_delimiter = ','
    mapping_file_delimiter = '\t'

    first_cols = opts.first_cols.split(",")
    last_cols = opts.last_cols.split(",")
    if opts.verbose:
        print "The following column(s) will be first in output:",str(first_cols)
        print "The following column(s) will be last in output:",str(last_cols)
    
    print "Input metadata files:"+opts.metadata_files
    if "," in opts.metadata_files:
        input_metadata_files = ",".split(opts.metadata_files)
    else:
        input_metadata_files = [opts.metadata_files]
    total_files = len(input_metadata_files)
    
    if "," not in opts.mapping_columns:
        #If multiple inputs, but only one mapping field, assume all inputs
        #will be mapped using that field
        mapping_fields = [opts.mapping_columns]*total_files
    else:
        mapping_fields = ",".split(opts.mapping_columns)
        if len(mapping_fields) != total_files:
            raise ValueError("If passing multiple, comma-separated files, you must EITHER pass only one mapping column (which will be used to join all tables) OR a comma-separated list of mapping columns, in the same order as the files they should be used to map.")
    
    #Load old QIIME mapping file.  Parse header line, then for each data line,
    #insert new fields just before description
    print "Loading input QIIME mapping file:",opts.input_mapping_file
    #The result starts as the old mapping file, then we add/update columns
    result = open(opts.input_mapping_file,'U')
    
    files_to_join = zip(input_metadata_files,mapping_fields)
    print "Files to join:",files_to_join
    for metadata_fp,mapping_col in files_to_join:
        #if "&&" in mapping_col:
        #    #Information from the mapping file should be concatenated
        #    #into a new column before adding new metadata
        #    old_mapping_file_lines =\
        #      add_merged_column_to_mapping(old_mapping_file_lines,\
        #      mapping_col.split("&&"), merged_col_delim)

        print "Loading new metadata from file:",metadata_fp
        metadata_file = open(metadata_fp,'U') 
    
        print "Generating new mapping file by joining metadata file %s on column %s" %(metadata_file,mapping_col)
        
        result = supplement_mapping_file(result,metadata_file,\
          mapping_col,first_cols=first_cols,last_cols=last_cols)
    
    #print "Result:", result
    i=0
    #Open output file
    print "Opening output file:",opts.output_mapping_file
    outfile = open(opts.output_mapping_file,'w+')
    for l in result:
        i+=1
        outfile.write(l)
        #print l.strip()
    print "Done. %i output lines saved to:%s" %(i,opts.output_mapping_file)
    outfile.close()

if __name__ == "__main__":
    main()
