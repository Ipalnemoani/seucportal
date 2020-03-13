# -*- coding: utf-8 -*-

import os
import json
import uuid
import pygal
# import datetime
import requests

from datetime import datetime
from functools import wraps
from base64 import b64encode
from pygal.style import DefaultStyle
from werkzeug import secure_filename
from werkzeug.urls import url_parse
from werkzeug.exceptions import RequestEntityTooLarge
from flask import g, Flask, render_template, request, url_for, Blueprint, Response, Markup
from flask import abort, flash, redirect, session, jsonify, current_app
from flask import make_response, send_from_directory, after_this_request, send_file
from flask_bootstrap import Bootstrap
from flask_login import current_user, login_user, logout_user, login_required


from app import app
from app.models import *
from app.schemas import *
#from app.forms import CreateTicketForm
from app.email import send_email
from app.modules.ldaplogin import LDAPLogin
from app.modules.dbportal import SEUCPortalDB
from app.modules.dbtaxi import TaxiPortalDB
from app.modules.taximodules import allowed_file, write_approval_file, create_taxi_report_to_download
from app.modules.encryptmodule import decrypt, encrypt
from app.modules.uploader import upload_file_to_server

from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import NoResultFound

apdata = PagesModel.query.order_by(PagesModel.idpages).all()

allpages = [page.routepage for page in apdata]

subpages_query = SubPagesModel.query

menus = {page.routepage : {"menuname": page.namepage,
                            "submenu": (subpages_query.filter_by(idmainpage=page.idpages)
                            .with_entities('routesubpage', 'namesubpage')
                            .all())} for page in apdata}

roles = {
        'IT /SEUC':allpages,
        'IT':allpages,
        'HR & GA Group /SEUC':[allpages[0], allpages[3], allpages[6]],
        'ALL':[allpages[0], allpages[3], allpages[5]],
        'CC':[allpages[0], allpages[5]]
        }

#surveys = Blueprint('surveys', __name__, template_folder='templates')
taxi = Blueprint('taxi', __name__, template_folder='templates')
#hms = Blueprint('hms', __name__, template_folder='templates')
#helpdesk = Blueprint('helpdesk', __name__, template_folder='templates')
#logistic = Blueprint('logistic', __name__, template_folder='templates')

portal_db = SEUCPortalDB(app.config['DB_NAME'])
#survdb = SurveyPortalDB(app.config['DB_SURVEYS_NAME'])
taxidb = TaxiPortalDB(app.config['DB_NAME'])
#hmsdb = HMSPortalDB(app.config['DB_NAME'])
#helpdeskdb = HelpDeskDB(app.config['DB_HELPDESK_NAME'])


def roles_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if f.__name__ not in roles[current_user.department]:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def browser_detection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        browser = request.user_agent.browser
        if browser == 'msie':
            return render_template('unsupported.html')
        return f(*args, **kwargs)
    return decorated_function


def check_authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.admin == 'no':
            return redirect(url_for('noauthorize'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
@browser_detection
def login():

    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        next_page = request.args.get('next')

        ldapserv = LDAPLogin()
        username = request.form['username']
        pwd = request.form['password']

        if not ldapserv.conn_to_ad(username, pwd):
            flash(ldapserv.MSGINFO, 'alert-danger')
        else:
            employee = ldapserv.find_employee_data()
            try:
                query = PortalUserModel.query
                user = query.filter_by(knox_id=username).first()

                if user is None:
                    try:
                        gencode = employee["employeeNumber"][0]
                    except IndexError:
                        gencode = 0000000000
                    user = PortalUserModel(
                                knox_id=employee["sAMAccountName"][0].strip(),
                                full_name=employee['description'][0].strip(),
                                department=employee['department'][0].strip(),
                                email=employee["mail"][0].strip(),
                                gencode=gencode.strip())
                    db.session.add(user)
                    db.session.commit()

                if user.department not in roles:
                    user.department = 'ALL'
                elif 'Agents' in user.department:
                    user.department = 'CC'
                login_user(user)

                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('dashboard')
                return redirect(next_page)
            except InterfaceError:
                flash(DB_ERROR_TITLE, 'alert-danger')
    return render_template('login.html', title='Sign In Potral', user='Guest')


@app.route('/dashboard')
@browser_detection
@login_required
def dashboard():
    return render_template('dashboard.html',
                            title='Dashboard',
                            active='dashboard',
                            roles=roles,
                            allpages=allpages,
                            menus=menus)


@app.route('/uploader', methods = ['GET', 'POST'])
@browser_detection
@login_required
@roles_required
def upload_file():
    if request.method == 'POST':
        files = request.files
        for i in files.keys():
            filename = secure_filename(files[i].filename)
            temp_file = os.path.join(TEMP_FILE_PATH, filename)
            files[i].save(temp_file)
        return 'file uploaded successfully'+' : '+temp_file


#@app.route('/', defaults={'page':1})
@app.route('/taxi', defaults={'page': 1, 'limit': 10, 'totalpages': 1, 'offset': 0}, methods=['GET', 'POST'])
@app.route('/taxi<int:page>', methods=['GET'])
@browser_detection
@login_required
@roles_required
def taxi(page, limit, totalpages, offset):
    if request.method == 'GET' and not request.args.get('module'):
        if request.args.get('page'):
            page = int(request.args.get('page'))

        trip_reasons = TaxiReasonsModel.query.all()
        taxi_vendors = TaxiVendorsModel.query.filter(TaxiVendorsModel.taxi_status==1).all()
        taxi_requests_query = TaxiRequestModel.query.filter_by(user_id=current_user.id)

        taxi_requests_qty = taxi_requests_query.count()
        if taxi_requests_qty > limit:
            totalpages = round((taxi_requests_qty / limit) + 0.45)
        if 1 < page <= totalpages:
            offset = limit*(page - 1)
        elif page < 1 or page > totalpages:
            return make_response(jsonify(message="error", status='No'))


        taxi_requests_query = taxi_requests_query.order_by(TaxiRequestModel.datenow.desc(),
                                                        TaxiRequestModel.dateoftrip.desc())
        taxi_requests_query = taxi_requests_query.offset(offset).limit(limit)

        taxi_schema = TaxiRequestSchema(many=True)
        taxi_data = taxi_schema.dump(taxi_requests_query)
        res = render_template('taxi/taxi_table.html', taxi_data=taxi_data, page=page)

        if request.args.get('pagination'):
            return make_response(jsonify(status='Ok', phtml=res))

        valext = app.config['ALLOWED_EXTENSIONS']
        fext = ""
        for ext in valext:
            fext += ".{},".format(ext)

        return render_template('taxi/taxi_main.html', title='Taxi', active='taxi',
                               roles=roles, allpages=allpages, menus=menus, page=page,
                               totalpages=totalpages, taxi_data=taxi_data, taxi_vendors=taxi_vendors,
                               trip_reasons=trip_reasons, fext=fext)

    elif request.method == 'POST':
        approval = None
        if 'approval' not in request.form:
            approval_file = request.files['approval']
            if approval_file and allowed_file(approval_file.filename):

                original_name = approval_file.filename
                extantion = original_name.rsplit('.', 1)[1].lower()

                prefix = 'approvalname'
                sufix = datetime.now().strftime("%Y%m%d%H%M%S%f")
                fullname = '{}_{}.{}'.format(prefix, sufix, extantion)

                filename = secure_filename(fullname)
                approval = TaxiApprovalsModel(user_id=current_user.id,
                                            approval_name=filename,
                                            approval_data=approval_file.read(),
                                            approval_original_name=original_name)
                db.session.add(approval)
                db.session.flush()
                db.session.commit()

        new_request = TaxiRequestModel(
                user_id = current_user.id,
                datenow = datetime.now().date(),
                taxi_company = request.form['taxi-company'].strip(),
                ticket_n = request.form['ticket-number'].strip(),
                dateoftrip = request.form['date'].strip(),
                timeoftrip = f"{request.form['start-time-trip']}-{request.form['end-time-trip']}",
                reason = request.form['reason'].strip(),
                destination = request.form['destination'].strip(),
                approval = approval,
                expance = request.form['expanse'].strip(),
                comment = request.form['comment'].strip(),
                fullname = current_user.full_name,
                email = current_user.email
                )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('taxi', page=page))
    return jsonify(status='false', error='Bad Request')


@app.route('/open_download_file', methods=['GET', 'POST'])
@app.route('/taxi/open_download_file', methods=['GET', 'POST'])
def open_download_file():

    if request.method == 'GET':
        filename = request.args['name']
        app_id = request.args['row']
        if taxidb.connect_to_db():
            appdata = taxidb.get_approval_data(app_id, filename)
            filedata = appdata[0]
            orig_app_name = appdata[1]
            if filename.rsplit('.', 1)[1].lower() == 'pdf':
                file_mymtype = 'application/octet-stream'
            else:
                file_mymtype = 'application/octet-stream'
            resp = current_app.response_class(filedata, mimetype=file_mymtype)
            resp.headers.set('Content-Disposition', 'inline', filename=filename)
            resp.headers.set('Content-Type', file_mymtype)
            resp.headers.set('Server','')

            return resp
    elif request.method == 'POST':
        jsondata = request.get_json()

        filename = jsondata['name']
        app_id = jsondata['row']

        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in app.config['IMAGE_EXTENSIONS']:
            if taxidb.connect_to_db():
                filedata = taxidb.get_approval_data(app_id, filename)[0]
                image = b64encode(filedata)
                return jsonify(content='img', btype=image.decode('ascii'))
        elif file_ext == 'pdf':
            return jsonify(content=file_ext, name=filename, rowid=app_id)
        elif file_ext == 'mht' or file_ext == 'msg' or file_ext == 'eml':
            if taxidb.connect_to_db():
                return jsonify(content=file_ext, name=filename, rowid=app_id)
    return jsonify(status='false', error='Bad Request')


@app.route('/edit_request', methods=['GET', 'POST'])
@browser_detection
@login_required
def edit_request():

    offset = 0
    limit = 10
    valext = app.config['ALLOWED_EXTENSIONS']
    fext = ""
    for ext in valext:
        fext += ".{},".format(ext)

    if request.method == 'GET':
        req_id = request.args['row']
        page = request.args['page']
        if taxidb.connect_to_db():
            trip_reasons = TaxiReasonsModel.query.all()
            request_data = TaxiRequestModel.query.get(req_id)

            request_schema = TaxiRequestSchema()
            request_data = request_schema.dump(request_data)
            res = render_template('taxi/edit_request_modal.html', request_data=request_data,
                                  trip_reasons=trip_reasons, fext=fext, req_id=req_id, page=page)
            return jsonify(status='ok', phtml=res, rowid=req_id)

    elif request.method == 'POST':

        approval_id = request.form['edit-approval_row']
        page = int(request.form['edit-request-page'])
        if page < 1 or page > 1:
            offset = limit*(page - 1)

        if request.files:
            approval_file = request.files['edit-approval']
            if approval_file and allowed_file(approval_file.filename):

                original_name = approval_file.filename
                extantion = original_name.rsplit('.', 1)[1].lower()

                prefix = 'approvalname'
                sufix = datetime.now().strftime("%Y%m%d%H%M%S%f")
                fullname = '{}_{}.{}'.format(prefix, sufix, extantion)

                filename = secure_filename(fullname)

                if not approval_id:
                    approval = TaxiApprovalsModel(user_id=current_user.id,
                                                approval_name=filename,
                                                approval_data=approval_file.read(),
                                                approval_original_name=original_name)
                    db.session.add(approval)
                    db.session.flush()
                    db.session.commit()
                    approval_id = approval.id
                else:
                    approval = TaxiApprovalsModel.query.get(approval_id)
                    approval.approval_name = filename
                    approval.approval_original_name = original_name
                    approval.approval_data = approval_file.read()
                    db.session.commit()

        request_id = request.form['edit-request-row']

        taxi_request = TaxiRequestModel.query.get(request_id)
        taxi_request.ticket_n = request.form['ticket-number'].strip()
        taxi_request.dateoftrip = request.form['date'].strip()
        taxi_request.timeoftrip = f"{request.form['start-time-trip']}-{request.form['end-time-trip']}"
        taxi_request.reason = request.form['reason'].strip()
        taxi_request.destination = request.form['destination'].strip()
        taxi_request.expance = request.form['expanse'].strip()
        taxi_request.comment = request.form['comment'].strip()
        taxi_request.approval = approval_id
        db.session.commit()

        taxi_query = TaxiRequestModel.query.filter_by(user_id=current_user.id)
        taxi_query = taxi_query.order_by(TaxiRequestModel.datenow.desc(),
                                        TaxiRequestModel.dateoftrip.desc())
        taxi_query = taxi_query.offset(offset).limit(limit)
        taxi_schema = TaxiRequestSchema(many=True)
        taxi_data = taxi_schema.dump(taxi_query)

        res = render_template('taxi/taxi_table.html', taxi_data=taxi_data, page=page)
        return make_response(jsonify(status='ok', phtml=res))
    return redirect(url_for('taxi', page=page))

@app.route('/taxi/adminpanel', defaults={'page':1, 'name':'', 'ticket':'', 'sdate':'', 'edate':''}, methods=['GET', 'POST'])
@browser_detection
@login_required
@check_authorize
def taxi_admin_panel(page, name, ticket, sdate, edate):
    if request.method == 'GET':
        limit = 10
        totalpages = 1

        if request.args:
            page = int(request.args['page'].strip())
            name = request.args['name'].strip()
            ticket = request.args['ticket'].strip()
            sdate = request.args['sdate'].strip()
            edate = request.args['edate'].strip()

        request_query = TaxiRequestModel.query

        if not sdate:
            sdate_query = request_query.with_entities(TaxiRequestModel.dateoftrip)
            min_sdate = sdate_query.order_by(TaxiRequestModel.dateoftrip).first()
            sdate = min_sdate[0]

        if not edate:
            edate = datetime.now().date()

        print('sdate: '+ str(sdate))
        request_query = TaxiRequestModel.query.join(PortalUserModel)
        query = request_query.filter(PortalUserModel.knox_id.like(f"%{name}%"),
                                    TaxiRequestModel.ticket_n.like(f"%{ticket}%"),
                                    TaxiRequestModel.dateoftrip >= sdate,
                                    TaxiRequestModel.dateoftrip <= edate)

        taxi_requests_qty = query.count()
        print(taxi_requests_qty)

        if taxi_requests_qty > limit:
            totalpages = round((taxi_requests_qty / limit) + 0.45)

        if page <= 1:
            offset = 0
        elif page > 1:
            offset = limit*(int(page) - 1)

        taxi_requests = query.order_by(TaxiRequestModel.id.desc()).offset(offset).limit(limit).all()
        #print(taxi_requests[0].id)
        res = render_template('taxi/taxi_admin_table.html', taxi_requests=taxi_requests, page=page)

        if request.args.get('pagination'):
            return make_response(jsonify(status='ok', phtml=res, pqty=totalpages))

        return render_template('taxi/taxi_admin.html', title='Taxi - Admin', active='taxi', roles=roles, allpages=allpages, menus=menus, totalpages=totalpages, page=page)

@app.route('/taxi/adminpanel/file')
@browser_detection
@login_required
@check_authorize
def taxifile_download():
    if taxidb.connect_to_db():
        print(request.args)
        knox_id = request.args['name']
        ticket = request.args['ticket']
        sdate = request.args['sdate']
        edate = request.args['edate']

        titles = ['ID', 'knoxID', 'CreateDate', 'TaxiCompany', 'TicketNumber', 'TripDate', 'TripTime', 'Reason', 'Destination', 'ApprovalName', 'Expance', 'Comment']
        taxidata = taxidb.get_admin_data_filters(knox_id, ticket, sdate, edate, 0, 1000000)

        fpath, filename = create_taxi_report_to_download(titles, taxidata, knox_id, ticket, sdate, edate)
        fsize = os.stat(fpath).st_size
        def generate():
            with open(fpath,'rb') as f:
                yield from f
            os.remove(fpath)

        resp = current_app.response_class(generate(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp.headers.set('Content-Disposition', 'attachment', filename=filename)
        resp.headers.set('Content-Length', fsize)
        resp.headers.set('Content-Type', 'application/octet-stream')
        resp.headers.set('Server','')

        return resp

@app.route('/taxi/addnote', methods=['POST'])
@browser_detection
@login_required
@check_authorize
def addnote():
    if request.method == 'POST':
        jsondata = request.get_json()
        if jsondata and taxidb.connect_to_db():
            rowid = jsondata['rowid']
            note = jsondata['note']
            taxidb.add_admin_note(note, rowid)
            return make_response(jsonify(status='ok'))

@app.route('/taxi/changestatus', methods=['GET'])
@browser_detection
@login_required
@check_authorize
def changestatus():
    if request.method == 'GET':
        if request.args and taxidb.connect_to_db():
            rowid = request.args['rowid']
            stat = request.args['stat']
            taxidb.change_status(stat, rowid)
            return make_response(jsonify(status='ok'))

@app.route('/taxi/statistic')
@browser_detection
@login_required
@check_authorize
def line_route():
    args = request.args
    knoxid = args['knoxid']
    sdate = args['sdate']
    edate = args['edate']
    if taxidb.connect_to_db():
        data = taxidb.count_taxi_company(knoxid, sdate, edate)

        pie_chart = pygal.Pie(inner_radius=.2, print_values=True, legend_box_size=14, height=275,
                              style=DefaultStyle(
                                            value_font_family='',
                                              value_font_size=15,
                                              value_colors=('white', 'white', 'white')
                                            )
                              )
        pie_chart.title = 'Taxi QTY Usage Rate for Specified Period.'

        line_chart = pygal.HorizontalBar(print_values=True, legend_box_size=14,
                                         height=275, value_formatter=lambda x: '{}0₴'.format(x),
                                         style=DefaultStyle(
                                              value_font_family='',
                                              value_font_size=15,
                                              value_colors=('white', 'white', 'white', 'white', 'white')
                                              )
                                         )
        line_chart.title = 'Total Amount by Taxi for Specified Period (in UAH)'

        for line in data:
            pie_chart.add(line[0], int(line[1]))
            line_chart.add(line[0], float(line[2]))

        reasons_data = taxidb.count_all_reasons(knoxid, sdate, edate)
        pie_reasons_chart = pygal.Pie(inner_radius=.2, print_values=True,
                                      legend_box_size=14, height=275,
                                      style=DefaultStyle(
                                          value_font_family='',
                                          value_font_size=15,
                                          value_colors=('white', 'white', 'white', 'white', 'white')
                                          )
                                      )
        pie_reasons_chart.title = 'Reasons Taxi Usage Rate for Specified Period (QTY)'


        reason_line_chart = pygal.HorizontalBar(print_values=True, legend_box_size=14, height=275,
                                                value_formatter=lambda x: '{}.00₴'.format(x),
                                                style=DefaultStyle(
                                                      value_font_family='',
                                                      value_font_size=15,
                                                      value_colors=('white', 'white', 'white', 'white', 'white')
                                                      )
                                                )
        reason_line_chart.title = 'Reasons Taxi Usage Rate for Specified Period (in UAH)'

        for line in reasons_data:
            pie_reasons_chart.add(line[0], int(line[1]))
            reason_line_chart.add(line[0], int(line[2]))

        data_cost_by_user = taxidb.count_qty_and_cost_by_user(sdate, edate)
        data_qty_by_user = taxidb.count_qty_by_user(sdate, edate)

        qty_data = len(data_qty_by_user)
        colors = tuple(['white' for i in range(qty_data)])

        bar_chart_qty = pygal.HorizontalBar(print_values=True, legend_box_size=10, height=275,
                                            style=DefaultStyle(
                                                value_font_family='',
                                                value_font_size=12,
                                                value_colors=colors)
                                            )
        bar_chart_qty.title = 'QTY Usage Taxi by Employee for Specified Period (TOP 10)'
        for line in data_qty_by_user:
            bar_chart_qty.add(line[0], [{'value':int(line[1])}])

        bar_chart_cost = pygal.HorizontalBar(print_values=True, legend_box_size=10, height=275,
                                             style=DefaultStyle(
                                                value_font_family='',
                                                value_font_size=12,
                                                value_colors=colors)
                                             )
        bar_chart_cost.title = 'Amount Usage Taxi by Employee for Specified Period (TOP 10)'
        for line in data_cost_by_user:
            bar_chart_cost.add(line[0], int(line[1]))

        chart = pie_chart.render_data_uri()
        chartline = line_chart.render_data_uri()
        barchart = bar_chart_qty.render_data_uri()
        barcostchart = bar_chart_cost.render_data_uri()
        reasonchart = pie_reasons_chart.render_data_uri()
        reason_uah = reason_line_chart.render_data_uri()

        res = render_template('taxi/taxi_statistic.html', chart=chart, chartline=chartline,
                              barchart=barchart, easonchart=reasonchart, reason_uah=reason_uah,
                              barcostchart=barcostchart, sdate=sdate, edate=edate)
        return make_response(jsonify(status='ok', phtml=res))

@app.route('/sendmail', methods=['GET'])
def sendmail():
    if request.method == 'GET':
        if request.args:
            if request.args['module'] == 'taxi':
                rowid = request.args['rowid']
                if taxidb.connect_to_db():
                    email_info = taxidb.get_email_data(rowid)
                    reciplist = [email_info[0]]

                    html_body = render_template('taxi/taxi_email.html', msg=email_info[1])
                    send_email('Taxi Portal: New Message from Administrator!',
                               sender=app.config['MAIL_DEFAULT_SENDER'], recipients=reciplist,
                               text_body='text_body', html_body=html_body)
                return make_response(jsonify(status='ok'))

@app.route('/noauthorize', methods=['GET'])
@browser_detection
@login_required
def noauthorize():
    return render_template('noauthorized.html', title='Noauthorized', active='dashboard',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/hms', methods=['GET'])
@browser_detection
@login_required
def hms():
    return render_template('noauthorized.html', title='HMS', active='hms',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/survey', methods=['GET'])
@browser_detection
@login_required
def survey():
    return render_template('noauthorized.html', title='Survey', active='survey',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/acm', methods=['GET'])
@browser_detection
@login_required
def acm():
    return render_template('noauthorized.html', title='ACM', active='acm',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/users', methods=['GET'])
@browser_detection
@login_required
def users():
    return render_template('noauthorized.html', title='Users', active='users',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/faq', methods=['GET'])
@browser_detection
@login_required
def faq():
    return render_template('noauthorized.html', title='FAQ', active='faq',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/attendance', methods=['GET'])
@browser_detection
@login_required
def attendance():
    return render_template('noauthorized.html', title='Attendance', active='attendance',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/helpdesk', methods=['GET'])
@browser_detection
@login_required
def helpdesk():
    return render_template('noauthorized.html', title='IT HelpDesk', active='helpdesk',
                           roles=roles, allpages=allpages, menus=menus)

@app.route('/exit')
def exit():

    session['logged_in'] = False
    session['permanent'] = False
    session["requested_url"] = "/"
    logout_user()
    return redirect(url_for('login'))
