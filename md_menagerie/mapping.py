from string import strip
from collections import defaultdict
from numpy import diff,interp,array,unique,mean
import matplotlib.pyplot as plt

class MappingTable():
    """Handle loading and manipulation of QIIME mapping files
    """
    def __init__(self,lines,field_delimiter="\t",comment_prefix="#"):
        
        #Load a table object from lines
        self.loadTableFromLines(lines,field_delimiter=field_delimiter,\
          comment_prefix=comment_prefix)

    
    def iterRows(self,row_names=None):
        """Iterate id,data tuples for each row"""
        
        for row_id,data in zip(self.RowIds,self.Data):
            if row_names is None:
                #Don't filter by row_names
                yield row_id,data
            elif row_id in row_names:
                yield row_id,data
    
    def iterRowData(self,row_names=None):
        """Iterate data values for each row
        row_names -- if a list is supplied only yield rows matching these names
        """

        for row_id,data in self.iterRows(row_names=row_names):
            yield data

    def iterCols(self,col_names=None,row_names=None):
        """Iterate id,data tuples for each column
        row_names -- if a list is supplied, use only rows with ids in the list
        
        """
        #if column names are not specified, return all columns
        if col_names is None:
            col_names = self.ColIds
        
        for col_id in col_names:
            data = []
            #Get data for this column from all rows
            for row in self.iterRowData(row_names):
                curr_data=row[self.ColIndices[col_id]]
                data.append(curr_data)
        
            yield col_id,data

    def iterColData(self,col_names=None,row_names=None):
        """Yields a list of data values for specified columns for each row
        col_names -- a list of column names.  Only yield data from these columns
            if not specified, yield all columns
        row_names -- a list of row names to include.  If not specified, use data from all rows
        """

        for col_id,col_data in self.iterCols(col_names,row_names):
            yield col_data

    
    def iterNumericCols(self,col_names,conversion_fn=float):
        """Yields tuples of numeric data for each point in col_list that can be converted to float

        cols -- a list of data columns with (mostly) numeric data
        example: ['pH','temp']

        limit_by_col -- limit to only rows with particular data vales
        """
           
        #Try to convert row data using conversion_fn
        for col in self.iterColData(col_names):
            try:
                converted_data = map(conversion_fn,col)
            except ValueError:
                #Bad data, must skip entire data point
                continue
            yield converted_data
    
    def iterNumericDataByRow(self,col_names,conversion_fn=float):
        
        #Try to convert row data using conversion_fn
        col_indices_of_interest = set(self.ColIndices[col] for col in col_names)
        for row in self.iterRowData():
            fields_of_interest =\
                [field for i,field in enumerate(row) if i in col_indices_of_interest]
            try:
                converted_data = map(conversion_fn,fields_of_interest)
                #All fields are GOOD (numeric) values -- SKIP
                yield converted_data
            except ValueError:
                continue


    def iterNonNumericDataByRow(self,col_names,conversion_fn=float):
        """Yields tuples of non-numeric data for each row where at least one of a set of specified columns cannot be converted to float

        col_names -- a list of header names for data columns with (mostly) numeric data
        example: ['pH','temp']

        limit_by_col -- limit to only rows with particular data vales

        conversion_fn -- a function to convert a field to a number. This function 
        relies on conversion_fn throwing a ValueError for non-numeric/ not convertable data.
        (as with e.g. the defautl float() function)
        """
           
        #Try to convert row data using conversion_fn
        col_indices_of_interest = set(self.ColIndices[col] for col in col_names)
        
        for row in self.iterRowData():
            fields_of_interest =\
                [field for i,field in enumerate(row) if i in col_indices_of_interest]
            try:
                converted_data = map(conversion_fn,fields_of_interest)
                #All fields are GOOD (numeric) values -- SKIP
                continue
            except ValueError:
                #Bad data, yield only the numeric cols
                converted_data = []
                for field in fields_of_interest:
                    try:
                        converted_field = conversion_fn(field)
                        converted_data.append(converted_field)
                    except ValueError:
                        converted_data.append(field)
                yield converted_data
    
    def splitByCol(self,cols):
        """Return a dict of new MappingTable objects, one for each unique value in col
        
        cols -- list of column to use in splitting the data.  
        New groups of data will be created, each keyed by the tuple
        """
        
        #Note that cols *must not* be a string
        if isinstance(cols,basestring):
            raise ValueError("splitByCol method needs a list of strings for input, not a naked str")
        col_indices = [self.ColIndices[col] for col in cols]
        
        row_id_collections = defaultdict(list)
        for row_id,row_data in self.iterRows():
            #We want a dict of  groups based on each unique value for our column
            group = tuple(row_data[col_idx] for col_idx in col_indices)        
            row_id_collections[group].append(row_id)

        #Now we want to generate a delimited table for each 
        #set of row ids
        text_collections = defaultdict(list)
        for group_id,row_ids in row_id_collections.iteritems():
            text_collections[group_id]=self.delimitedSelf(limit_to_rows=row_ids)

        result={}
        for group_id,lines in text_collections.iteritems():
            result[group_id] = MappingTable(lines,field_delimiter=self.FieldDelimiter,\
              comment_prefix=self.CommentPrefix)
        
        return result

    def interpolate(self,col,reference_col):
        """Interpolate non-numerical values of col using linear piece-wise regression on reference col
        
        col -- column to interpolate (only non-numerical values will be interpolated
        reference_col -- column to use as a reference for interpolated values
        """
        print "COL TO INTERPOLATE:",col
        print "reference_col:",reference_col
        paired_numeric_vals = self.iterNumericDataByRow(col_names=[col,reference_col])
        non_numeric_vals = [ref_col for col,ref_col in self.iterNonNumericDataByRow([col,reference_col])]
        print "non_numeric_x_vals:", non_numeric_vals
        #print "paired_numeric_data:",[x for x in paired_numeric_vals]
        x_vals = []
        for x_val in non_numeric_vals:
            print "x_val",x_val
            try:
                x_val = float(x_val)
                x_vals.append(x_val)
            except ValueError:
                print "Could not convert %s to float" %x_val
                continue
                
        x = array(x_vals) 
        #default sort is by first element which is what we want.
        #numpy.interp requires that x_ref be sorted in increasing order
        sorted_numeric_vals = sorted(paired_numeric_vals)
        paired_numeric_series = zip(*sorted_numeric_vals)
        if paired_numeric_series:
            y_ref,x_ref = paired_numeric_series
            x_ref,y_ref = map(array,average_points_by_x(x_ref,y_ref))
        else:
            #No reference data!
            return [],[]
        #Quickly check to ensure we are sorted cleanly
        assert all(diff(x_ref)) > 0
        #manually convert to list because array() doesn't handle generators
        print "INPUT INTERPOLATION DATA:",x,x_ref,y_ref
        try:
            interpolated_y = interp(x,x_ref,y_ref)
        except TypeError,e:
            raise ValueError("Bad input to interpolate:",x,x_ref,y_ref)
        print "X:",x
        print"interpolated_y:",interpolated_y
        return x,interpolated_y
    
    def selectRowsByValue(self,target_value,ref_col,conversion_fn=float,sides='both'):
        """yield the row(s) that have values in ref_col closest to a given target value
        target_value -- the value that rows should match (in the reference column)
        ref_col -- the name of the column that is matched (e.g. 'pH')
        conversion_fn -- the function that converts raw values in the reference column.
          the conversion_fn should throw ValueError if the value cannot be converted (this allows skipping of 'Unknown' or NULL columns).  NOTE: one use of conversion_fn is to allow accurate comparison of date columns.
        sides -- can be set to 'greater_than','both',or 'less_than'. 
          If both, select rows using only the absolute difference.  
          If 'greater_than', limit the selection to rows that are larger than the target_value. 
          If 'less_than', limit the selection to rows that are smaller than the target_value. 
        """
         
        ref_col_idx = self.ColIndices(ref_col)
        
        row_ids = []
        row_vals = []
        for row_id,row in self.iterRows():
            raw_row_val = row[ref_col_idx]
            
            try:
                row_val = conversion_fn(raw_row_val)
            except ValueError:
                #skip values that can't be converted (e.g. 'Unknown')
                continue
            if sides == 'greater_than' and row_val <= target_val:
                #we want only rows above target_val
                continue
            if sides == 'less_than' and row_val >= target_val:
                #we want only rows below target_val
                continue
            row_ids.append(row_id)
            row_vals.append(row_val)
        
        row_vals = array(row_vals)
        diffs = abs(row_vals - target_value)
        min_row_indices = argmin(row_vals)
        #Not just selecting these from an array of row_ids
        # because row_ids may be non-numeric
        min_row_ids = [row_ids[i] for i in list(min_row_indices)]             
        return min_row_ids
 
    
    def updateColByInterpolation(self,col,ref_col):
        """Update a column of self.Data using interpolation of col on ref_col"""
        #Find values that need updating because they lack a 

        non_numeric_entries =\
          [data for data in self.iterNonNumericDataByRow([col,ref_col])]
        x_series,y_series = self.interpolate(col,ref_col)
        update_dict = {x:y for x,y in zip(x_series,y_series)}
        return self.updateCol(col,ref_col,update_dict,conversion_fn=float)

        
    def updateCol(self,col,ref_col,updates,conversion_fn=None,ignore_vals=["Unknown","NULL","unknown"]):
        """Update self.Data for col with values from update_dict

        col -- the name of a column to update (i.e. overwrite)
        ref_col -- the name of a reference column to use in adding the updates
        updates -- a dict of {ref_col_value:col_value} pairs.  Rows with reference
        column values equal to a key in the dict will be set to the value of the dict
        conversion_fn -- a function to apply to each value in ref_col before
        matching to the keys of updates
        """
        if ref_col not in self.ColIndices:
            err_text = "%s is not a valid column.  Valid columns are: %s"%(ref_col,self.ColIndices.keys())
            raise ValueError(err_text)
        ref_val_idx = self.ColIndices[ref_col]
        curr_val_idx = self.ColIndices[col]

        for i,row in enumerate(self.Data):
            
            reference_val = row[ref_val_idx]
            curr_data_val = row[curr_val_idx]
            #NOTE: do not update values not in update dict
            #This is accomplished by updating these values
            # with the reference valiiue
            if conversion_fn is not None and reference_val not in ignore_vals:
                reference_val = conversion_fn(reference_val)
            
            update_val = str(updates.get(reference_val,curr_data_val))
            self.Data[i][curr_val_idx]=update_val
        
        return self

    def rowMatches(self,row,criteria={}):
        """Return True if row fields specified in criteria match values in criteria
        row -- a single data row (list of fields)
        criteria -- a dict of field names and ok values.  Example: {'pH':7.0,'host':'human'}"""
        #TODO: change criteria to a criterion function 
        criteria_by_indices = {self.ColIndices[k]:v  for k,v in criteria.items()}
        
        for idx in criteria_by_indices.keys():
            #NOTE: currently the only criterion available is equality
            if row[idx] != criteria_by_indices[idx]:
                return False

        #If we haven't returned False by failing a criterion, row is OK
        #Note that this implies we return True on an empty criteria dict
        return True
    
    def rowsMatching(self,criteria={}):
        """Return all rows matching criteria"""
        for row_id,row in self.iterRows():
            if self.rowMatches(row,criteria):
                yield row_id,row
   
    def delimitedSelf(self,limit_to_rows=None,write_header=True,write_comments=True):
        """Output a delimited version of self"""
        delimiter = self.FieldDelimiter
        
        result = []
        
        if write_header:
            header_line = "%s%s\n" %(self.CommentPrefix,\
                delimiter.join(self.HeaderFields))
            result.append(header_line)
        
        if write_comments:
            for comment in self.OtherCommentLines:
                result.append(comment) #must already start with comment prefix
        
        for fields in self.iterRowData(limit_to_rows):
            data_line = "%s\n" %(delimiter.join(fields))
            result.append(data_line)

        return result

    def mergedColsAsText(self,cols,merged_col_delimiter="_"):
        """output a list of lines mapping sample ids to a set of merged columns
        cols_to_merge -- list of header names for columns to merge
        """
        all_col_data = []
        col_names = []
        for col_name,col_vals in self.iterCols(cols):
           all_col_data.append(col_vals)
           col_names.append(col_name)

        yield merged_col_delimiter.join(col_names)+"\n"
        print "all_col_data:",all_col_data
        
        for merged_row_items in zip(*all_col_data):
            print "merged_row_items:",merged_row_items
            curr_result=merged_col_delimiter.join(map(str,merged_row_items))+"\n"
            yield curr_result 
    
    def loadTableFromLines(self,lines,field_delimiter="\t",comment_prefix="#",
        row_id_field_idx=0,header_row=0):
        """Populate a mapping table object from lines
        
        Notably, SampleIds are currently preserved in self.Data
        """
        
        header=lines[header_row]

        self.FieldDelimiter=field_delimiter
        self.CommentPrefix=comment_prefix
        
        self.HeaderFields=\
          header.lstrip(comment_prefix).split(field_delimiter)
        
        self.HeaderFields=[h.strip() for h in self.HeaderFields]
        self.OtherCommentLines=[]
        self.RowIndices={}
        self.ColIndices={}
        self.RowIds=[]
        self.ColIds=self.HeaderFields
        self.Data = []
        for line in lines[1:]:
            #Non-header comment lines are saved without processing
            if line.startswith(comment_prefix):
                self.OtherCommentLines.append(line)
                continue
            
            fields = [f.strip() for f in line.split(field_delimiter)]
            
            #if a non-comment line, add to self.Data
            self.Data.append(fields)
            i=len(self.Data) - 1   
            #using this instead of enumerate because we skip some lines
            
            row_id = fields[row_id_field_idx]
            self.RowIds.append(row_id)

            #Map identifier to this index
            self.RowIndices[row_id] = i
            
            for j,field in enumerate(fields):
                #Map column identifier to this index
                col_id = self.HeaderFields[j]
                self.ColIndices[col_id]=j

            

def average_points_by_x(x,y):
    """Return  sorted x,y with unique values of x, averaging y-values for each x value"""
    x_to_y_vals = defaultdict(list)
    for xi,yi in zip(x,y):
        x_to_y_vals[xi].append(yi)
    unique_x = list(unique(x))
    averaged_y = [mean(x_to_y_vals[x]) for x in unique_x]
    return unique_x,averaged_y


def make_criterion_from_text(text):
    """Returns a criterion function from text.  The function always accepts to values: input and criteria and returns True if input matches critiera
    
    Grammar:
    basic equality (basic shortcut):
    'property:ok_value' #returns True if property is exactly equal to value
    
    'property = value' #equivalent to 'property:value'
    'property > value' #returns True if property is greater
    'property < value' #return True if property is lower than value
     
    """
    pass
