import xlsxwriter

def export_to_excel(name_of_file = 'export.xlsx', sheet_name = 'Sheet1', col_names = None, datarows = None, table_name=None, datecolumns=[]):

    """ 
        Module for export data in Excel.
        Parameters:
                name_of_file (str) - name of file with extantion *.xls or *.xlsx
                sheet_name (str) - name of sheet
                col_names (list) - list of column names, default (None). If default, names of columns are numerate.
                datarows (list) - list or tuple of lists with data
    """

    if not datarows:
        raise ValueError('datarows can not be None')
        return False

    wb = xlsxwriter.Workbook(name_of_file)
    ws = wb.add_worksheet(sheet_name)
    ws.hide_gridlines(2)
    
    formatname = wb.add_format({'font_size':16, 'bold':True, 'bottom':1, 'align':'left',})
    formattitle = wb.add_format({'bold':True, 'bg_color':'#99ccff', 'border':2, 'align':'center',})
    dateformat = wb.add_format({'num_format': 'yyyy-mm-dd', 'border':1})
    timeformat = wb.add_format({'num_format': 'hh:mm:ss', 'border':1})
    cellsformat = wb.add_format({'border':1})
    title_rowformat = wb.add_format({'bottom':1})

    start_row = 1

    if table_name:
        start_row = 4
        ws.set_row(1, 15, title_rowformat)
        ws.write(1, 0, table_name, formatname)

    if not col_names:
        len_columns = len(datarows[0])
        col_names = [i for i in range(len_columns)]
    else:
        len_columns = len(col_names)

    for i in range(len_columns):
        ws.set_column(start_row-1, i, 15)
        ws.write(start_row-1, i, col_names[i], formattitle)
        for i, k in enumerate(datarows):
            for j in range(len(k)):
                if j in datecolumns:
                    ws.write(i + start_row, j, k[j], dateformat)
                elif j == 3 or j == 5:
                    ws.write(i + start_row, j, k[j], timeformat)
                else:
                     ws.write(i + start_row, j, k[j], cellsformat)
    try:
        wb.close()
    except PermissionError:
        print('Error! The file is open. To create a report, please, close the file.')
        return False
    
    return True

if __name__ == "__main__":
    export_to_excel(datarows=[['test', 'test', 'test']], table_name='Test Table Because We have Name!')
