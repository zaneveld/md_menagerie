from mapping import MappingTable
"""
Brainstorming a way to make a parallel sets plot similar to the one here in d3.js:
Like a Sankey diagram, except that the memory for one metadata category (dimension)
Is preserved across each layer of the diagram: http://www.jasondavies.com/parallel-sets/

Here is a link to an example with Sankey diagrams: http://fineo.densitydesign.org/custom/vis/index.php?tablename=set14062427826&submit=Visualize



Here are the steps I think we would need:

    1. Read in the mapping file and parse
    2. Identify the categories of interest
    2.5 probably filter?
    3. Build a contingency table for each value of each category
    4. Draw a line for each category of interest at an arbitrarily spaced y-coordinate
    5. Each y-coordinate gets a :
"""


def sum_mapping_by_category(mapping):
    pass

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


def sets_by_category_combinations(mapping,categories):
    """
    """
    #Iterate over categories
    all_sets = []
    for category in categories:
        #Save the counts for data values in this category
        sets_this_cat = []
        data_this_cat = mapping.iterRowData(col_names=category)
        print "data_this_cat:",[d for d in data_this_cat]
        

    sets = [{cat:set() for cat in categories)}]
    


    

if __name__ == "__main__":
    example_data = open("../test_data/parallel_sets_test_data.txt","U") 
    mapping_table = MappingTable(example_data.readlines())
    
    #Set up some generic plot parameters
    cols = mapping_table.ColIds
    data = mapping_table.Data
    color_by = 'Dead'
    parallel_sets_plot
