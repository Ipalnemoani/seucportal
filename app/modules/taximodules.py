# -*- coding: utf-8 -*-

import os
import datetime
import xlsxwriter


from app import app
from app.modules.export_excel import export_to_excel


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def write_approval_file(data, filename):
    
    fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(fpath, 'wb') as pdffile:
        pdffile.write(data)
        return fpath

    
def create_taxi_report_to_download(titles, data, knox_id, ticket, sdate, edate):
    uploadfile_dir = app.config['UPLOAD_FOLDER']
    
    if not knox_id:
        knox_id = 'All'
    
    if not ticket:
        ticket = 'All'

    if not sdate and not edate:
        dates = 'All'
    elif not sdate:
        dates = 'To {}'.format(edate)
    elif not edate:
        dates = 'From {} to Today'.format(sdate)
    else:
        dates = '{} - {}'.format(sdate, edate)
    taxi_title = 'SEUC Taxi Report | Employee: {}, Ticket: {}, Trip Dates: {}'.format(knox_id, ticket, dates)

    prefix = 'TaxiReport'
    sufix = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    filename = '{}_{}.xlsx'.format(prefix, sufix)
    filepath = os.path.join(uploadfile_dir, filename)
    
    download_file = export_to_excel(filepath, col_names=titles,
                                    datarows=data, table_name=taxi_title,
                                    datecolumns=[2, 5])
    if download_file:
        return (filepath, filename)
