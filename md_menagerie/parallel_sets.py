
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
    pass

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

    


    


