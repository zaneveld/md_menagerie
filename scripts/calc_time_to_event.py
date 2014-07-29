#!/usr/bin/env python
# File created on 15 Jul 2011
from __future__ import division
from warnings import warn

__author__ = "Jesse Zaneveld"
__copyright__ = "Copyright 2013, The HERBVRE Project"
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
script_info = {}
script_info['brief_description'] = "Given a mapping file with metadata specifying a date for each sample and observed event metadata (e.g. disease, death, etc), generate a realtive time to the first occurence of the event (if any) in that sample"
script_info['script_description'] =\
"""
Analysis of complex ecological experiments often involves attempting to understand changes in the microbial community that preceded or followed after a stochastic event.  For example, if some individuals spontaneously develop disease, it may be interesting to test whether predictable microbiota changes precede that change.

"""

script_info['script_usage'] = [("","","")]
script_info['output_description']= "Output is metadata table (for use with add_metadata_to_mapping_file.py)"
script_info['required_options'] = [\
make_option('-i','--input_mapping_file',type="existing_filepath",\
  help='the input QIIME format mapping file '),\
  make_option('--time_column',\
  help='column that specifies the start time for the experiment in yyyymmdd format.'),\
  make_option('--event',\
  help='metadata column and value that specifies the event of interest in the format.  For example:  HealthState:DarkSpotSyndrome'),\
  make_option('--individual_column',default='Individual',\
  help='metadata column and value that specifies the individual. [Default:%default] ')\
]
script_info['optional_options'] = [\
 make_option('-o','--output_file',type="new_filepath",\
   default=None,help='the output filepath for the new mappinging file, updated with metadata [default: based on input filename]')]
script_info['version'] = __version__

def relative_date_info_from_mapping(lines,time_column,\
  event_column, event_state,individual_column="Individual"):
    """Return elapsed time from an event for each sample based on current and start times
    
    lines -- lines of the mapping file
    time_column -- the column in the mapping file containing a concatenated date
    event_column -- the column to study to find events
    event_state -- the state for the event in the column.  E.g. perhaps only timepoints where healthstate = Diseased are of interest
    individual_column -- if events are per-individual, only count the first occurence of the event for this individual.
    """
    
    #Method

    #Create defaultdict and scan all lines, building up lists of event by individual.
    #For each individual, scan each line
    

    #yield "#SampleID\t\n"
    
    required_columns = [c for c in [time_column,event_column,individual_column] if c is not None]
    lines = [l for l in lines] #need to cache so that we can iterate over lines multiple times :(
    #but mapping files are usually small-ish so perhaps not such a big deal
    events_by_individual = defaultdict(list)
    all_entries_by_individual = defaultdict(list)
    yield "SampleID","DaysAfter%s" %event_state,"WeeksAfter%s" %event_state
    #First, map all events to individuals
    for i,line in enumerate(lines):
        if i==0 and line.startswith('#'):
            headers = line.lstrip('#').strip('\n').split('\t')
            header_index_dict = {h:i for i,h in enumerate(headers)} 
            for col in required_columns:
                if col not in header_index_dict.keys():
                    raise ValueError("The column '%s' isn't in the mapping file header:%s. Is the column present and spelled correctly?"%(col,str(sorted(header_index_dict.keys()))))

        elif line.startswith('#'):
            continue
        else:
            #We're in a data line
            fields = line.strip('\n').split('\t')
            event_concatenateddate = fields[header_index_dict[time_column]]
            individual = fields[header_index_dict[individual_column]]
            all_entries_by_individual[individual].append(event_concatenateddate)
            curr_event_state = fields[header_index_dict[event_column]]
            if curr_event_state == event_state: 
                events_by_individual[individual].append(event_concatenateddate)

    
    first_event_by_individual = defaultdict(list)
    for individual in events_by_individual.keys():
        first_event = min(map(int,events_by_individual[individual]))
        first_event_by_individual[individual] = first_event

    for i,line in enumerate(lines):
        if line.startswith('#'):
            continue
        
        sample_id = fields[header_index_dict['SampleID']]
        fields = line.strip('\n').split('\t')
        individual = fields[header_index_dict[individual_column]]
        event_concatenateddate = fields[header_index_dict[time_column]]
        
        first_event_day = first_event_by_individual.get(individual,None)
        if first_event_day is None:
            continue
        
        #Otherwise calc difference in days
        time_delta  = date(*split_concatenated_date(str(event_concatenateddate))) - date(*split_concatenated_date(str(first_event_day)))
        yield sample_id,time_delta.days,round(time_delta.days/7)

     
def split_concatenated_date(concatenated_date):
    """Split a concatenated date of the form yyyymmdd into years,months,days"""
    if len(concatenated_date) !=8:
        raise ValueError("String %s isn't eight characters long (len = %i).  Concatenated dates must be yyyymmdd (example:20120817)"%(concatenated_date,str(len(concatenated_date))))

    year = concatenated_date[:4]
    month = concatenated_date[4:6]
    day = concatenated_date[6:]
    return map(int,[year,month,day])
    



def main():
    option_parser, opts, args =\
       parse_command_line_parameters(**script_info)
  
    
    metadata_file_delimiter = ','
    mapping_file_delimiter = '\t'

    #New strategy:
    #Open output file
    print "Opening output file:",opts.output_file
    outfile = open(opts.output_file,'w+')

    
    #Load old QIIME mapping file.  Parse header line, then for each data line,
    #insert new fields just before description
    print "Loading input QIIME mapping file:",opts.input_mapping_file
    mapping_file = open(opts.input_mapping_file,'U')
    
    event_column,event_state = opts.event.split(':')
    time_column = opts.time_column
    
    result = relative_date_info_from_mapping(mapping_file,time_column,event_column, event_state,individual_column="Individual")

    
    #print "Result:", result
    for l in result:
        line_to_print = "\t".join(map(str,l))+"\n"
        outfile.write(line_to_print)
        print line_to_print.strip()
    
    print "Done. Output saved to:",opts.output_file
    outfile.close()

if __name__ == "__main__":
    main()
