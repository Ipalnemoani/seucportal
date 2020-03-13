# -*- coding: utf-8 -*-

import os
import json


from app import app, db, ma, login
from flask_login import UserMixin
from datetime import datetime, timedelta
from marshmallow_sqlalchemy import fields


@login.user_loader
def load_user(id):
    return PortalUserModel.query.get(int(id))


class PortalUserModel(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'portal'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    knox_id = db.Column(db.String(45))
    email = db.Column(db.String(45))
    full_name = db.Column(db.String(45))
    gencode = db.Column(db.String(45))
    department = db.Column(db.String(45))
    division = db.Column(db.String(45), default='')
    status = db.Column(db.Integer, default=1)
    admin = db.Column(db.Boolean, unique=False, default=False)

    worktime = '09:00:00-18:00:00'
    userinfo = f"<div>\
                <b><span class='glyphicon glyphicon-home'></span> Department:</b> {department}\
                <br>\
                <b><span class='glyphicon glyphicon-briefcase'></span> Devision:</b> {division}\
                <br>\
                <b><span class='glyphicon glyphicon-envelope'></span> Email:</b> {email}\
                <br>\
                <b><span class='glyphicon glyphicon-time'></span> Worktime:</b> {worktime}\
                </div>"

    taxi_creator = db.relationship('TaxiRequestModel',
                                    backref=db.backref('taxi_creator', lazy=True),
                                    foreign_keys='TaxiRequestModel.user_id')
    approval_user = db.relationship('TaxiApprovalsModel',
                                    backref=db.backref('approval_user', lazy=True),
                                    foreign_keys='TaxiApprovalsModel.user_id')

    def __repr__(self):
        return "<Name {}>".format(self.full_name)

    def create_userinfo(self):
        return f"<div>\
                    <b><span class='glyphicon glyphicon-home'></span> Department:</b> {self.department}\
                    <br>\
                    <b><span class='glyphicon glyphicon-briefcase'></span> Devision:</b> {self.division}\
                    <br>\
                    <b><span class='glyphicon glyphicon-envelope'></span> Email:</b> {self.email}\
                    <br>\
                    <b><span class='glyphicon glyphicon-time'></span> Worktime:</b> {self.worktime}\
                </div>"


class PagesModel(db.Model):
    __tablename__ = 'pages'
    __table_args__ = {'schema': 'portal'}

    idpages= db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    routepage = db.Column(db.String(255))
    namepage = db.Column(db.String(255))
    subpage = db.relationship('SubPagesModel',
                            backref=db.backref('subpages', lazy=True),
                            foreign_keys='SubPagesModel.idmainpage')

    def __init__(self, routepage, namepage):
        self.routepage = routepage
        self.namepage = namepage

    def __repr__(self):
        return "Page Name: {}".format(self.namepage)


class SubPagesModel(db.Model):
    __tablename__ = 'subpages'
    __table_args__ = {'schema': 'portal'}

    idsubpage = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    idmainpage = db.Column( db.Integer,
                            db.ForeignKey(PagesModel.idpages),
                            nullable=False)
    routesubpage = db.Column(db.String(255))
    namesubpage = db.Column(db.String(255))

    def __init__(self, idmainpage, routesubpage, namepage):
        self.idmainpage = idmainpage
        self.routesubpage = routesubpage
        self.namesubpage = namesubpage

    def __repr__(self):
        return "SubPage Name: {}".format(self.namesubpage)


class TaxiVendorsModel(db.Model):
    __bind_key__ = 'taxi'
    __tablename__ = 'taxi_vendor'
    __table_args__ = {'schema': 'taxi'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    taxi_name = db.Column(db.String(255), nullable=False)
    taxi_status = db.Column(db.Integer, unique=False, default=1)


class TaxiReasonsModel(db.Model):
    __bind_key__ = 'taxi'
    __tablename__ = 'reason_name'
    __table_args__ = {'schema': 'taxi'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)


class TaxiApprovalsModel(db.Model):
    __bind_key__ = 'taxi'
    __tablename__ = 'approvals'
    __table_args__ = {'schema': 'taxi'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(PortalUserModel.id), nullable=False)
    approval_name = db.Column(db.String(255))
    approval_data = db.Column(db.LargeBinary())
    approval_original_name = db.Column(db.String(255))


class TaxiRequestModel(db.Model):
    __bind_key__ = 'taxi'
    __tablename__ = 'test_request_info'
    __table_args__ = {'schema': 'taxi'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(PortalUserModel.id), nullable=False)
    datenow = db.Column(db.Date)
    taxi_company = db.Column(db.String(255))
    ticket_n = db.Column(db.String(255))
    dateoftrip = db.Column(db.Date)
    timeoftrip = db.Column(db.String(255))
    reason = db.Column(db.String(255))
    destination = db.Column(db.String(255))
    approval = db.Column(db.Integer, db.ForeignKey(TaxiApprovalsModel.id), nullable=False)
    expance = db.Column(db.String(255))
    comment = db.Column(db.Text)
    status = db.Column(db.Boolean, unique=False, default=False)
    fullname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    admin_comment = db.Column(db.String(255))

    approval_data = db.relationship("TaxiApprovalsModel", backref=db.backref("approve", uselist=False))
    employee = db.relationship("PortalUserModel", backref=db.backref("employee", uselist=False))

    def __repr__(self):
        return "Request №: {}".format(self.id)




if __name__ == '__main__':
    pass
