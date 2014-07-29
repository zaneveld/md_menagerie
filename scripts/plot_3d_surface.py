
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
try:
    from cogent.util.option_parsing import parse_command_line_parameters, make_option
except ImportError:
    raise ImportError("Could not import option parsing from cogent.util.option_parsing.  Is PyCogent installed (you can run this script within MacQIIME or the QIIME virtualbox to make use of a 'pre-packaged' PyCogent installation)")
from string import strip
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
from numpy import arange,sqrt,sin,array,meshgrid,interp,linspace
from numpy.random import uniform, seed
from collections import defaultdict
from mpl_toolkits.axes_grid1 import make_axes_locatable


PLOT_TYPES = ['3d_surface','contour']


script_info = {}
script_info['brief_description'] = "Generate 3d plots of metadata from a QIIME mapping file."
script_info['script_description'] =\
"""
"""

script_info['script_usage'] = [("","Generate a 3d plot of temperature x month x equitability for control samples found in the mapping file herbivore_mapping_r15_with_alpha.txt.  Save to output file 3d_plot_test.png",\
        "%prog -m ./test_script_data/herbivore_mapping_r15_with_alpha.txt -c 'HCOM_temp_5m,month,equitability_even_500_alpha' -f 'treatment:Control' -o ./test_script_data/3d_plot_test.png")]
script_info['output_description']= "Output is a new QIIME mapping file, with metadata from one or more metadata files added."
script_info['required_options'] = [\
make_option('-m','--input_mapping_file',type="existing_filepath",\
  help='the input QIIME format mapping file.'),\
  make_option('-c','--mapping_columns',\
  help='A comma-separated list of metadata headers to be used for the x,y, and z axes. For example: "month,temp,pH" would use month on the x axis,temp on the y-axis, and pH on the z-axis"'),\
]
script_info['optional_options'] = [\
 make_option('-o','--output_file',type="new_filepath",\
   default='3d_plot.png',help='the output filepath for graph. The extension will determine matplotlib output format (so you can specify my_plot.png for images or my_plot.pdf for vector) [default: %default]'),\
 make_option('-f','--column_filter',\
         default=None,help='Specify a set of filters to apply to columns.  Filters should be comma-separated pairs of header names and the value to be retained.  Example: -f "treatment:Control,host_taxon_abbreviation:Ss" [default:%defualt]'),\
  make_option('-p','--plot_type',\
  default='3d_surface',help='Comma-separated list of type of plot to make. If combined with split_subplots_by_col, one figure of each type will be made, with the specified subplots.  Available plot types:'+ ','.join(PLOT_TYPES)+'. [default:%default]'),\
  make_option('--x_limits',\
  default=None,help='Specify a min and max value for all x axes as a comma separated pair. Example: --x_limits "0.0,100.0" limits x to between 0.0 and 100.0 [default:minimum and maximum value in that series]'),\
  make_option('--y_limits',\
    default=None,help='Specify a min and max value for all y axes as a comma separated pair. Example: --y_limits "0.0,100.0" limits x to between 0.0 and 100.0 [default:minimum and maximum value in that series]'),\
  make_option('--z_limits',\
    default=None,help='Specify a min and max value for all z axes as a comma separated pair. Example: --z_limits "0.0,100.0" limits x to between 0.0 and 100.0 [default:minimum and maximum value in that series]'),\
  make_option('-s','--split_subplots_by_col',default=False,\
  help='If a column name is supplied, make one subplot per unique value in a given column.[default:%default]'),\
  make_option('--interpolate_y',default=False,action='store_true',\
  help='Interpolate non-numerical y values using x values prior to plotting.[default:%default]')
]

script_info['version'] = __version__


def parse_column_filter(filter_as_text):
    """Convert a string describing column fitlers into a dictionary of filters"""
    
    #Handle case where empty (None) filter provided
    if not filter_as_text:
        filter_set = {}
        return filter_set
    
    filters=filter_columns_and_values.split(",")
    filter_set={}
    for f in filters:
        col,ok_value = f.split(":")
        filter_set[col]=ok_value
    return filter_set

def parse_user_header_list(header_names, delimiter=",",expected_n_headers=3):
    """parse a user string specifying a list of mapping file headers to use
    headers -- a user string of header names 
    delimiter -- the delimiter separating headers in the string
    expected_n_headers -- the expected number of headers (error if a different number is specified)
    """
 
    #Read header
    user_specified_headers = header_names.split(delimiter)
    if len(user_specified_headers) != expected_n_headers:
        partial_example_headers = ['header']* expected_n_header
        full_example_headers = delimiter.join([h+str(i) for h,i in enumerate(partial_example_headers)])
        raise ValueError("Must specify %i  headers separated by '%s' to plot.  Example: '%s'" %(expected_n_headers,delimiter,full_example_headersi))
    return user_specified_headers

def apply_filters_to_fields(fields,filters_by_idx={},verbose=True):
    """Return True if field text exactly matches filter_by_idx for each field index"""
    for idx in filters_by_idx.keys():
        if str(fields[idx]) != filters_by_idx[idx]:
            return False
    
    #If we didn't fail a filter then the data look OK; return True
    #Also return True if an empty filters_by_idx dict was specified (i.e. no filtering)
    return True

def interpolate_y_on_x(x_data,y_data,z_data,strict=False):
    """Interpolate y_data from x_data"""
    coords_to_interpolate=[]
    reference_coords=[]
    reference_values=[]
    
    z_vals = []
    for x,y,z, in sorted(zip(x_data,y_data,z_data)):
        try:
            x=float(x)
            z=float(z)
        except ValueError:
            #Skip Unknown/NULL x-values...can't interpolate or use as reference
            #print "Skipping this data point (couldn't convert to float)",(x,y,z)
            continue
        z_vals.append(z)
        #All valid reference values should be in the output
        coords_to_interpolate.append(x)
        try:
            y=float(y)
        except ValueError:
            #print "Omiting this data point from reference (couldn't convert y value to float):",y
            #Note that we need to interpolate a y value for the current x
            continue
        
        #If all data values are ok, add to reference dataset
        reference_coords.append(x)
        reference_values.append(y)
        #z_by_xy[(x,y)]=z 
    #print "Coords to interpolate:",coords_to_interpolate
    #print "reference coords:",reference_coords
    #print "reference valus:",reference_values
    
    if not len(reference_coords) or not len(reference_values):
        if not strict:
            err_msg = "No interpolation performed on this data series...no reference values available"
            print err_msg
            return x_data,y_data,z_data
        else:
            raise ValueError(err_msg)
    
    interpolated_y_vals = interp(array(coords_to_interpolate),array(reference_coords),array(reference_values))
    x_vals = coords_to_interpolate
            
    return x_vals,interpolated_y_vals,z_vals 

def extract_3d_plot_data_from_mapping(lines,x_header,y_header,z_header,filter_set=None,jitter=True,eps=0.1,verbose=True):
    """Extract metadata columns from QIIME mapping file lines
    lines -- lines of the QIIME mapping file.  The first line must contain the headers
    x_header -- name of the header for the x-axis
    y_header -- name of the header for the y-axis
    z_header -- name of the header for the z-axis

    jitter -- if true, jitter points slightly to prevent duplicate x,y valus from being skipped (despite different z values) in
    Delauney triangulation

    eps -- the amount to randomly shift x,y points.  Usually set to a trivially low number
    """
 
    #infile_header = infile.next().split("\t")
    #infile_header = lines.next().split("\t")
    infile_header = lines[0].split("\t")
    x_idx = infile_header.index(x_header)
    y_idx = infile_header.index(y_header)
    z_idx = infile_header.index(z_header)
    
    #Make filters work according to index
    filters_by_idx = {}
    
    if filter_set:
        filters_by_idx={}
        for f in filter_set.keys():
            idx = infile_header.index(f)
            filters_by_idx[idx]=filter_set[f]

    #Read data
    
    x=[]
    y=[]
    z=[]
    for i,line in enumerate(lines):
        if line.startswith('#'):
            #comment line, skip
            continue

        fields=line.split("\t")
        if filters_by_idx:
            passes_filter = apply_filters_to_fields(fields,filters_by_idx)
        else:
            passes_filter = True

        if passes_filter is False:
            if verbose:
                print "Skipping.  Field: %s != filter: %s" %(fields[idx],filters_by_idx[idx])
            continue
           
        curr_x = fields[x_idx]
        curr_y = fields[y_idx]
        curr_z = fields[z_idx]
       
        if verbose:
            print "data line %i:"%i,curr_x,curr_y,curr_z
        x.append(curr_x)
        y.append(curr_y)
        z.append(curr_z)

    if not len(x) or not len(y) or not len(z):
        raise ValueError("All data points filtered out! Try less restrictive errors and check filters match data file")
    return x,y,z



def data_series_to_floats(data,verbose=False):
    """convert a dict of dicts of data to floating point, skipping entries that are strings"""
    result = defaultdict(dict)
    
    for series_name,series_values in data.items():
        new_x = []
        new_y = []
        new_z = []
        
        for x,y,z in zip(series_values['x'],series_values['y'],series_values['z']):
            try:
                curr_x = float(x)
                curr_y = float(y)
                curr_z = float(z)
            except ValueError:
                if verbose:
                    print "Skipping data line %i: one or more values could not be converted to float. key" %(i,key)
                continue
            new_x.append(curr_x)
            new_y.append(curr_y)
            new_z.append(curr_z)
        
        
        result[series_name]['x']=new_x
        result[series_name]['y']=new_y
        result[series_name]['z']=new_z
        
        #Copy over other values
        for key,value in data[series_name].items():
            if key not in ['x','y','z']:
                result[series_name][key] = value 
    
    return result

def jitter_data(series,eps=1e-6):       
    result = [x + uniform(-eps,eps) for x in series]
    return result 

def jitter_data_series(data,eps=1e-6):
    result=defaultdict(dict)
    #print "DATA:",data

    for series_name,series_values in data.items():
        #print "Series name, series_values:",series_name,series_values
        for key,value in data[series_name].items():
            if key in ['x','y','z']:
                value=jitter_data(value)
            #levae other entries like 'x_header' intact
            result[series_name][key]=value
    return result

def extract_multiple_series_from_mapping(lines,index_col,x_header,y_header,z_header,filter_set=None,jitter=True,eps=0.1,min_data_points=5,verbose=True):
    """Extract x,y,z data for multiple data series from mapping file lines.  Returns a dict keyed by series value, with dicts of x,y,z coordinates
    lines -- QIIME mapping file lines
    index_col -- the column on which to split series.
    """
    header_line = infile.next()
    infile_header = header_line.split("\t")
    index_col_idx = infile_header.index(index_col)

    lines_by_index = defaultdict(list)
    for line in lines:
        fields = line.split("\t")
        index_field = fields[index_col_idx]

        #Ensure the header line is present in all line collections
        if len(lines_by_index[index_field]) == 0:
            lines_by_index[index_field].append(header_line)
        lines_by_index[index_field].append(line)
    
    result = defaultdict(dict) 
    
    for series_name,series_lines in lines_by_index.items():
        try:
            x,y,z = extract_3d_plot_data_from_mapping(series_lines,x_header,y_header,z_header,filter_set,\
              jitter,eps,verbose)   
        except ValueError,e:
            print "Skipping series: %s.  Got ValueError %s.  Likely too few datapoints within series." %(series_name,e)
            continue
        if len(x) < min_data_points or\
          len(y) < min_data_points or\
          len(z) < min_data_points:
          
            print "Skipping data series: %s.  Too few data points.  len(x):%i,len(y):%i,len(z):%i." %(series_name,len(x),len(y),len(z))
            continue   
        #Ensure x,y,z have data

        result[series_name]["x"]=x
        result[series_name]["y"]=y
        result[series_name]["z"]=z
        result[series_name]["x_header"]=x_header
        result[series_name]["y_header"]=y_header
        result[series_name]["z_header"]=z_header
    
    return result

def interpolate_each_series(data,axis_to_interpolate='y'):
    """interpolate y values for each data series
    data -- a dict of dicts of lists, keyed by series name, then 'x','y','z'
      example:  data = {'control':{'x':[0.0,0.5,1.0],'y':['0.0','Unknown','2.1'],z=[2.0,3.2,1.7]}}
    """
    result = defaultdict(dict)
    for series_name,series_data in data.items():

        #Copy over non-data dictionary entries
        for key,value in series_data.items():
            if key not in ['x','y','z']:
                result[series_name][key]=value
        x = series_data['x']
        y = series_data['y']
        z = series_data['z']
        if not len(x) or not len(y) or not len(z):
            raise ValueError("Cannot interpolate:  one or more of x,y,z is empty. len(x) =%i,len(y)=%i,len(z)=%i" %(len(x),len(y),len(z)))
        if axis_to_interpolate == 'y':
            #print "len x:",len(x)
            #print "len y:",len(y)
            #print "len z:",len(z)
            xi,yi,zi = interpolate_y_on_x(series_data['x'],series_data['y'],series_data['z'])
            #print "len xi:",len(list(xi))
            #print "len yi:",len(list(yi))
            #print "len zi:",len(list(zi))
            result[series_name]['x']=xi
            result[series_name]['y']=yi
            result[series_name]['z']=zi
        else:
            raise NotImplementedError("Only interpolation on y is currently supported")
    return result


def interpolate_irregular_data(x,y,z,x_steps=20,y_steps=20):
    """Translate irregularly spaced data to a regular grid using Delauney triangulation (i.e. matplotlib's griddata() functioN)"""

    # define grid.
    xi = linspace(min(x),max(x),x_steps)
    yi = linspace(min(y),max(y),y_steps)
    zi = griddata(x,y,z,xi,yi)
    return xi,yi,zi

def make_3d_surface_plot(x,y,z,xi,yi,zi,n_points,\
  x_header,y_header,z_header,eps=1e-6,title=None,fig=None,ax=None,\
  x_min=None,x_max=None,y_min=None,y_max=None,z_min=None,z_max=None):
    
    """Make a matplotlib figure from evenly spaced data 
    Returns a surface object

    xi -- evenly spaced (usually interpolated) version of the x points
    yi -- evenly spaced (usually interpolated) version of the y points
    zi -- evenly spaced (usually interpolated) version of the z points
    
    n_points -- number of original data points
    
    x_header -- header for the x-axis
    y_header -- header for the y-axis
    z_header -- header for the z-axis
    
    fig -- if supplied, add the plot to this figure. 
    (By default a new figure is made)
    sublot -- if supplied, switch to this subplot before plotting
    ax -- if supplied, use this axis to plot (must be a 3d axis)
    """
    # grid the data for plotting
    xig,yig=meshgrid(xi,yi)
    if fig is None:
        fig = plt.figure()

    #Note that for multipart figures the subplot is implicit in the axis
    #so we don't need to know subplot specifically
    if ax is None:
        ax = fig.gca(projection='3d')
    
    #Set maximum and minimum values
    #TODO: ugly and repetitive.  Revise as a dict?
    if x_min is None:
        x_min = min(x)
    if y_min is None:
        y_min = min(y)
    if z_min is None:
        z_min = min(z)
    
    if x_max is None:
        x_max = max(x)
    if y_max is None:
        y_max = max(y)
    if z_max is None:
        z_max = max(z)
    
    
    surf = ax.plot_surface(xig, yig, zi, rstride=1, cstride=1, cmap=cm.afmhot,\
      vmin=z_min,vmax=z_max,linewidth=0.1, antialiased=True)
    ax.set_xlim(x_min,x_max)
    ax.set_ylim(y_min,y_max)
    ax.set_zlim(z_min, z_max)
    ax.set_xlabel(x_header)
    ax.set_ylabel(y_header)
    ax.set_zlabel(z_header)
    
    #cbar_ticks = linspace(z_min,z_max,15.0,endpoint=True)
    #fig.colorbar(surf, shrink=0.5, aspect=5,use_gridspec=True,ticks=cbar_ticks)
   
    #fig.colorbar(surf, shrink=0.5, aspect=5,use_gridspec=True)
    fig.colorbar(surf, shrink=0.5, aspect=5,use_gridspec=True,format='%1.2g')
    if title is not None:
        ax.set_title(title)
    return fig


def output_3d_surface_plot(outfile,x,y,z,x_header,y_header,z_header,title=None,\
   x_min=None,x_max=None,y_min=None,y_max=None,z_min=None,z_max=None):
    """Make a 3d surface plot of x,y,z data
    outfile -- location to write figure
    x -- a list of x values for points
    y -- ditto for y values
    z -- the same for z values
    """
    
    n_points=len(zip(x,y))
    
    #generate evenly spaced, interpolated data
    xi,yi,zi = interpolate_irregular_data(x,y,z)
    
    #Generate the figure
    fig = make_3d_surface_plot(x,y,z,xi,yi,zi,n_points,\
      x_header=x_header,y_header=y_header,z_header=z_header,title=title,\
      x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,z_min=z_min,z_max=z_max)
    #plt.show() 
    plt.savefig(outfile)



def output_contour_plot(outfile,x,y,z,x_header,y_header,z_header,title=None,\
  x_min=None,x_max=None,y_min=None,y_max=None,z_min=None,z_max=None):
    """Make a combined scatter and contour plot, interpolating irregularly spaced data"""
    
    n_points=len(zip(x,y))
    xi,yi,zi = interpolate_irregular_data(x,y,z)
    #fig = make_contour_plot(x,y,z,xi,yi,zi,x_header,y_header,z_header,title)
    fig = make_contour_plot(x,y,z,xi,yi,zi,x_header,y_header,z_header,title=title,fig=fig,ax=ax,\
                  x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,z_min=z_min,z_max=z_max)
    plt.savefig(outfile)
   

def make_contour_plot(x,y,z,xi,yi,zi,x_header,y_header,z_header,title=None,fig=None,ax=None,\
  x_min=None,x_max=None,y_min=None,y_max=None,z_min=None,z_max=None):
    """Make a contour plot with color coding for the z-axis"""
    
    #Set maximum and minimum values
    #TODO: ugly and repetitive.  Revise as a dict?
    if x_min is None:
        x_min = min(x)
    if y_min is None:
        y_min = min(y)
    if z_min is None:
        z_min = min(z)

    if x_max is None:
        x_max = max(x)
    if y_max is None:
        y_max = max(y)
    if z_max is None:
        z_max = max(z)

    if fig is None:
        fig = plt.figure()
    if not ax:
        ax = plt.subplot(1,1,1)

    n_levels = 10
    contour_levels = linspace(z_min, z_max, n_levels)
    CS = ax.contour(xi,yi,zi,contour_levels,linewidths=0.5,colors='k')
    #CS = ax.contourf(xi,yi,zi,15,cmap=plt.cm.afmhot,\
    #  vmax=abs(zi).max(), vmin=-abs(zi).max())
    
    CS = ax.contourf(xi,yi,zi,contour_levels,cmap=plt.cm.afmhot)
    

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", "5%", pad="3%")
    #cbar_ticks = linspace(z_min,z_max,15.0,endpoint=True)
    #cbar = plt.colorbar(CS, cax=cax,ticks=cbar_ticks)
    cbar = plt.colorbar(CS,cax=cax,format='%1.2g')
    cbar.set_clim(vmin=z_min,vmax=z_max)
    # plot data points.
    ax.scatter(x,y,marker='o',c='b',s=5,zorder=10)
    
    #Set axis bounds
    ax.set_xlim(x_min,x_max)
    ax.set_ylim(y_min,y_max)
    
    #Set axis labels
    ax.set_xlabel(x_header)
    ax.set_ylabel(y_header)
    if z_header:
        cbar.set_label(z_header)

    if title is not None:
        ax.set_title(title)
    return fig 
    
def output_multipart_figure(outfile,datasets,x_header,y_header,z_header,plot_types=['3d_surface'],title=None,fig=None,min_data_points=5,\
        x_min=None,x_max=None,y_min=None,y_max=None,z_min=None,z_max=None,verbose=False):
    """Output multipart figure with many subplots of mixed type"""
    
    
    total_subfigures = len(datasets) * len(plot_types)
    n_rows = len(datasets)
    n_cols = len(plot_types)
    if fig is None:
        aspect_ratio = float(n_rows)/float(n_cols)
        figsize = plt.figaspect(aspect_ratio)
        figsize[0] *= n_rows
        figsize[1] *= n_rows
        #raise ValueError("FIGURE SIZE:%s" %figsize)
        fig = plt.figure(1,figsize=figsize)
        fig.patch.set_facecolor('white')
    #Otherwise new subplots will be added to the current figure
    
    
    curr_subplot = 1
    
    for i,dataset in enumerate(datasets.items()):
        series_name,series_data = dataset
        if verbose:
            print "Plotting dataset %i" %(i)
        x,y,z = series_data["x"],series_data["y"],series_data["z"]
        n_points = len(zip(x,y))
        if len(x) < min_data_points or \
          len(y) < min_data_points or \
          len(z) < min_data_points:
              print "Skipping data series:%s.  Too few data points: %i,%i,%i" %(series_name,len(x),len(y),len(z))
              continue
        xi,yi,zi = interpolate_irregular_data(x,y,z)
        if verbose:
            print "Plot types:",plot_types 
        for j,plot_type in enumerate(plot_types):
            #matplotlib sublots are evily indexed from 1
            
            title_text = " %s %s  plot (n=%i)" %(series_name,plot_type,len(x))
            subplot=(i,j,1)
            if plot_type == "contour":
                if verbose:
                    print "Adding contour subplot:",i+1,j+1,1
                ax = fig.add_subplot(n_rows,n_cols,curr_subplot)
                make_contour_plot(x,y,z,xi,yi,zi,x_header,y_header,z_header,title=title_text,fig=fig,ax=ax,\
                  x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,z_min=z_min,z_max=z_max)
            
            elif plot_type == "3d_surface":
                if verbose:
                    print "Adding 3d subplot:",i+1,j+1,1
                ax=fig.add_subplot(n_rows,n_cols,curr_subplot,projection="3d")
                make_3d_surface_plot(x,y,z,xi,yi,zi,n_points,x_header,y_header,z_header,title=title_text,fig=fig,ax=ax,\
                  x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,z_min=z_min,z_max=z_max)
            
            curr_subplot +=1
    
    
    #fig.tight_layout(pad=2.0) 
    fig.subplots_adjust(wspace=0.31,hspace=0.15)
    #plt.show()
    fig.savefig(outfile)
 
 
if __name__ == "__main__":
    option_parser, opts, args =\
      parse_command_line_parameters(**script_info)

    infile = open(opts.input_mapping_file,"U")
    outfile = opts.output_file
    headers_to_plot=opts.mapping_columns
    filter_columns_and_values= opts.column_filter #example 'treatment:control'

    filter_set = parse_column_filter(filter_columns_and_values)
    user_specified_headers = parse_user_header_list(headers_to_plot,delimiter=",",expected_n_headers=3)
    
    #There must be three headers:  bind them to x,y,z
    x_header,y_header,z_header = user_specified_headers
    
    split_on_col = opts.split_subplots_by_col
    if split_on_col is  False:
        data_series = defaultdict(dict)
        x,y,z = extract_3d_plot_data_from_mapping(infile.readlines(),x_header,y_header,z_header,\
            filter_set=filter_set,jitter=True,eps=1e-6,verbose=opts.verbose)
        data_series["all data"]["x"]=x
        data_series["all data"]["y"]=y
        data_series["all data"]["z"]=z
    else:
        data_series=extract_multiple_series_from_mapping(infile,split_on_col,\
          x_header,y_header,z_header,filter_set=filter_set,jitter=True,eps=1e-6,verbose=opts.verbose)
    
    if opts.interpolate_y:
        data_series = interpolate_each_series(data_series)
    
    data_series = data_series_to_floats(data_series)

    jitter=True #TODO make a commandline option
    if jitter:
        data_series=jitter_data_series(data_series,eps=1e-6)

    #Plot types to make
    plots_to_make = opts.plot_type.split(",")
    for plot_type in plots_to_make:
        if plot_type not in PLOT_TYPES:
            raise ValueError("'%s' is not a supported plot type.  Valid choices are:%s" %(plot_type,",".join(PLOT_TYPES)))
    
    
    
    if opts.x_limits is not None:
        x_min,x_max = map(float,opts.x_limits.split(",")) 
    else:
        x_min,x_max = (None,None)
    if opts.y_limits is not None:
        y_min,y_max = map(float,opts.y_limits.split(",")) 
    else:
        y_min,y_max = (None,None)
    
    if opts.z_limits is not None:
        z_min,z_max = map(float,opts.z_limits.split(",")) 
    else:
        z_min,z_max = (None,None)
    
    output_multipart_figure(outfile,data_series,x_header,y_header,z_header,plot_types=plots_to_make,\
      x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,z_min=z_min,z_max=z_max,verbose=opts.verbose)

    #Save plot to outfile
    #plt.clf()
    #if '3d_surface' in plots_to_make :
    #    output_3d_surface_plot(outfile+"_3d_plot.png",x,y,z,x_header,y_header,z_header)
    #if 'contour':
    #    output_contour_plot(outfile+"_contour.png",x,y,z,x_header,y_header,z_header)
