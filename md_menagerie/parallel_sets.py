
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



"""
Brainstorming a way to make a parallel sets plot similar to the one here in d3.js:
Like a Sankey diagram, except that the memory for one metadata category (dimension)
Is preserved across each layer of the diagram: http://www.jasondavies.com/parallel-sets/

"""

from md_menagerie.mapping import MappingTable
from collections import defaultdict


def parallel_sets_from_mapping(mapping_table,categories):
    """Given a MappingTable object, construct parallel sets for specified cols
    
    mapping_table -- an md_menagerie MappingTabe
    categories -- a list of categories
    """
    #First calculate sets for top level categoreies
    top_level_sets = get_top_level_sets_from_mapping(mapping_table,categories)

    #Now calculate parallel_sets from this dictionary
    parallel_sets_from_set_dict(set_dict,categories)

def parallel_sets_from_dict_of_set_dicts(dict_of_set_dicts,categories):
    """Calculate a list of parallel sets from a dict of dicts of sets of sampleids

    dict_of_set_dicts --  a dict of dicts.  Outer level dict keys are mapping table 
      categories.  Inner level dicts are keyed by the values for each category.
      Values of the inner dicts are sets of sampleids.
      Exampe:  if there is one category called 'Temp' with two values 'high' and 'low',
      dict_of_set_dicts could be {'Temp':{'high':set(['s1','s2']),'low':set(['s3','s4'])}}

    categories -- a list of categories.  (['Temp'] in the above example)
    
    Typical input has multiple categories in set_dict.  The function
    calculates sets of ids that are shared by adjacent categories in the list
    of categories (this may seem arbitrary, but adjacent categories must
    be joined in the plot, so we need the width of adjacent, but not non-adjacent
    sets)

    The returned 'levels' of parallel sets will be in the form of a list
    of dicts of sets.
    """
    levels = []  #Corresponding to the levels of the plot

    for curr_level,category in enumerate(categories):
        if curr_level == 0: 
            levels.append(dict_of_set_dicts[category])
            #Don't intersect any other sets since this is the top level
            continue
        else:
            #In a lower level.  We need to find sets intersecting with
            #each piece of the previous level
            print "LEVELS:",levels
            print "CURR LEVEL:",curr_level
            print "CURR CATEGORY:",category
            prev_level_data = levels[curr_level-1]
            curr_level_data = dict_of_set_dicts[category]
            new_entries = intersect_two_set_dicts(prev_level_data,curr_level_data)
            levels.append(new_entries)
    return levels
            
def intersect_two_set_dicts(d1,d2):
    """Create a dict of intersections from two dicts of sets
    
    d1 -- a dict of sets  
    d2 -- another dict of sets (typically will have common items)

    NOTE: Which dict is assigned to d1 vs. d2 will affect the outcome- 
    the resulting dict will have keys that
    are tuples, with d1 keys first and d2 keys second.
    """
    result = {}
    for k1,v1 in d1.iteritems():
        for k2,v2 in d2.iteritems():
            new_key = (k1,k2)
            new_values = v1.intersection(v2)
            result[new_key]=new_values
    return result
     



def get_top_level_sets_from_mapping(mapping_table,categories):
    """Construct top level sets from a mapping file

    For example, if mapping categories 'TissueLoss' and 'Temp'
    are of interest, construct a dict like:
    {'TissueLoss':{'Yes':set(['s1','s2']),'No':set(['s3','s4']),
     'Temp':{'High':set(['s1','s4']),'Low':set(['s2','s3'])}}}
    """


    top_level_sets = {}
    for category in categories:
        curr_sets = defaultdict(set)
        col_data = mapping_table.iterCols(col_names = [category])
        for col_id,fields in col_data:
            row_ids_by_field = zip(mapping_table.RowIds,fields)
            for row_id,label in row_ids_by_field:
                curr_sets[label].add(row_id)
        
        top_level_sets[category] = dict(curr_sets)
        
    
    
    
    return top_level_sets

def parallel_sets_plot(data,categories,color_by=None,\
    category_properties={},subcategory_properties={},
    hspace=20.0,vspace=40.0):
    """Generate a parallel sets diagram
    data -- 
    categories -- list of categories to plot.
    category_properties -- a dictionary setting properties (matplotlib kwargs)
      for any category in categories.  For example if one column is 'treatment' and one
      column is 'gender', properties could be set for 'treatment', 'gender',
      '
    subcategory_properties -- a dictionary setting properties (matplotlib kwargs)
    for subcategories.  A subcategory is a tuple of specific values ( 
    For example if one column is 'gender' and another is 'treatment'
    a valid entry might be subcategory_properties = {('men','treatment'):{'facecolor':'red'},
    {('men','placebo'):{'facecolor':'blue'}
    

    Output: 
    Each column in categories will be represented by a horizontal row.
    

    The row will space out categories by the hspace value 
    (reduces visual clutter)
    
    
    """
    print "Categories:",categories
    print "Color by:", color_by
    
    #Start with the first category
    #Categories on horizontal axis
    horizontal_size = hspace * len(categories)
    vertical_size = vspace

    figure = ()
    plot = ([0,0],'r')

    


    


