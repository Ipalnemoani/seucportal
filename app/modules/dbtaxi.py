# -*- coding: utf-8 -*-

import json
import mysql.connector


from app import app
from mysql.connector import errorcode
from datetime import datetime, timedelta


from app.modules.dbportal import SEUCPortalDB


class TaxiPortalDB(SEUCPortalDB):

    def __init__(self, dbname):
        SEUCPortalDB.__init__(self, dbname)

    def get_qty_rows(self, user):
        sql = """   SELECT COUNT(test_request_info.user_id)
                    FROM taxi.test_request_info
                    WHERE test_request_info.user_id = %s """
        self.cursor.execute(sql, (user, ))
        return self.cursor.fetchone()[0]

    def get_taxi_vendors_names(self):
        sql = """   SELECT taxi_vendor.taxi_name
                    FROM taxi.taxi_vendor
                    WHERE taxi_vendor.taxi_status = 1"""
        self.cursor.execute(sql)
        return [taxi[0] for taxi in self.cursor.fetchall()]

    def get_reason_names(self):
        sql = """   SELECT reason_name.name
                    FROM taxi.reason_name """
        self.cursor.execute(sql)
        return [reason[0] for reason in self.cursor.fetchall()]

    def get_requests_taxi_by_user(self, user, offset, limit):
        sql = """   SELECT  test_request_info.id,
                            test_request_info.datenow,
                            test_request_info.taxi_company,
                            test_request_info.ticket_n,
                            test_request_info.dateoftrip,
                            test_request_info.timeoftrip,
                            test_request_info.reason,
                            test_request_info.destination,
                            approvals.approval_name,
                            test_request_info.expance,
                            test_request_info.comment,
                            test_request_info.status,
                            test_request_info.admin_comment,
                            approvals.id,
                            approvals.approval_original_name
                    FROM taxi.test_request_info
                    LEFT JOIN taxi.approvals
                    ON test_request_info.approval = approvals.id
                    WHERE test_request_info.user_id = %s
                    ORDER BY test_request_info.datenow DESC,
                            test_request_info.dateoftrip DESC
                    LIMIT %s, %s
                    """
        self.cursor.execute(sql, (user, offset, limit))
        data = self.cursor.fetchall()
        self.connection.close()
        return data

    def insert_approval_file(self, user_id, file_name, file_data, original):
        sql = """   INSERT INTO taxi.approvals VALUES ('', %s, %s, %s, %s) """
        self.cursor.execute('SET GLOBAL max_allowed_packet=67108864')
        self.cursor.execute(sql, (user_id, file_name, file_data, original))
        self.connection.commit()
        row_id = self.cursor.lastrowid
        self.cursor.execute('SET GLOBAL max_allowed_packet=1048576')
        self.connection.commit()
        return row_id

    def get_approval_data(self, app_id, filename):
        sql = """   SELECT approvals.approval_data,
                            approvals.approval_original_name
                    FROM taxi.approvals
                    WHERE approvals.id = %s
                    AND approvals.approval_name = %s """
        self.cursor.execute(sql, (app_id, filename))
        data = self.cursor.fetchone()
        self.connection.close()
        return data

    def insert_trip_request(self, *data):
        values = '%s, '*13
        sql = """   INSERT INTO taxi.test_request_info (
                                test_request_info.user_id,
                                test_request_info.datenow,
                                test_request_info.taxi_company,
                                test_request_info.ticket_n,
                                test_request_info.dateoftrip,
                                test_request_info.timeoftrip,
                                test_request_info.reason,
                                test_request_info.destination,
                                test_request_info.approval,
                                test_request_info.expance,
                                test_request_info.comment,
                                test_request_info.fullname,
                                test_request_info.email
                            )
                    VALUES ({0}) """.format(values[:-2])
        self.cursor.execute(sql, data)
        return self.connection.commit()

    def get_requests_taxi_by_id(self, rowid):
        sql = """   SELECT
                            test_request_info.taxi_company,
                            test_request_info.ticket_n,
                            test_request_info.dateoftrip,
                            test_request_info.timeoftrip,
                            test_request_info.reason,
                            test_request_info.destination,
                            approvals.approval_name,
                            test_request_info.expance,
                            test_request_info.comment,
                            approvals.id,
                            approvals.approval_original_name
                    FROM taxi.test_request_info
                    LEFT JOIN taxi.approvals
                    ON test_request_info.approval = approvals.id
                    WHERE test_request_info.id = %s
                    """
        self.cursor.execute(sql, (rowid,))
        data = self.cursor.fetchone()
        self.connection.close()
        return data

    def update_approval_file(self, app_name, orig_name, app_data, rowid):
        sql = """   UPDATE taxi.approvals
                    SET approvals.approval_name = %s,
                        approvals.approval_original_name = %s,
                        approvals.approval_data = %s
                    WHERE approvals.id = %s """
        self.cursor.execute(sql, (app_name, orig_name, app_data, rowid))
        self.connection.commit()

    def update_request_info(self, *data):
        sql = """   UPDATE taxi.test_request_info
                    SET test_request_info.ticket_n = %s,
                        test_request_info.dateoftrip = %s,
                        test_request_info.timeoftrip = %s,
                        test_request_info.reason = %s,
                        test_request_info.destination = %s,
                        test_request_info.approval = %s,
                        test_request_info.expance = %s,
                        test_request_info.comment = %s
                    WHERE test_request_info.id = %s
                    """
        self.cursor.execute(sql, data)
        self.connection.commit()
        return

    def get_admin_qty_rows(self):
        sql = """   SELECT COUNT(test_request_info.user_id)
                    FROM taxi.test_request_info """
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_data_for_admin(self, offset=0, limit=10):
        sql = """   SELECT  test_request_info.id,
                            users.knox_id,
                            test_request_info.datenow,
                            test_request_info.taxi_company,
                            test_request_info.ticket_n,
                            test_request_info.dateoftrip,
                            test_request_info.timeoftrip,
                            test_request_info.reason,
                            test_request_info.destination,
                            approvals.approval_name,
                            test_request_info.expance,
                            test_request_info.comment,
                            test_request_info.status,
                            test_request_info.admin_comment,
                            approvals.id as app_id,
                            approvals.approval_original_name,
                            test_request_info.email
                    FROM taxi.test_request_info
                    LEFT JOIN taxi.approvals
                    ON test_request_info.approval = approvals.id
                    LEFT JOIN portal.users
                    ON test_request_info.user_id = users.id
                    ORDER BY test_request_info.id DESC,
                            test_request_info.dateoftrip DESC
                    LIMIT %s, %s
            """
        self.cursor.execute(sql, (offset, limit))
        data = self.cursor.fetchall()
        self.connection.close()
        return data

    def get_admin_data_filters(self, knoxid, ticket, sdate, edate, offset=0, limit=10):

        if not sdate:
            s = """ SELECT MIN(test_request_info.dateoftrip)
                    FROM taxi.test_request_info
                """
            self.cursor.execute(s)
            sdate = self.cursor.fetchone()[0]

        if not edate:
            edate = datetime.now().date()

        sql = """   SELECT  test_request_info.id,
                            users.knox_id,
                            test_request_info.datenow,
                            test_request_info.taxi_company,
                            test_request_info.ticket_n,
                            test_request_info.dateoftrip,
                            test_request_info.timeoftrip,
                            test_request_info.reason,
                            test_request_info.destination,
                            approvals.approval_name,
                            test_request_info.expance,
                            test_request_info.comment,
                            test_request_info.status,
                            IFNULL(test_request_info.admin_comment, '') as admin_comment,
                            approvals.id as app_id,
                            approvals.approval_original_name,
                            test_request_info.email
                    FROM taxi.test_request_info
                    LEFT JOIN taxi.approvals
                    ON test_request_info.approval = approvals.id
                    LEFT JOIN portal.users
                    ON test_request_info.user_id = users.id
                    WHERE users.knox_id like %s AND test_request_info.ticket_n like %s AND test_request_info.dateoftrip BETWEEN %s AND %s
                    ORDER BY test_request_info.id DESC
                    LIMIT %s, %s """
        self.cursor.execute(sql, ('%'+knoxid+'%', '%'+ticket+'%', sdate, edate, offset, limit))
        data = self.cursor.fetchall()
        self.connection.close()
        return data

    def get_filter_qty_rows(self, knoxid, ticket, sdate, edate):
        print(sdate, edate)
        if not sdate:
            s = """ SELECT MIN(test_request_info.dateoftrip)
                    FROM taxi.test_request_info
                """
            self.cursor.execute(s)
            sdate = self.cursor.fetchone()[0]

        if not edate:
            edate = datetime.now().date()

        sql = """   SELECT COUNT(test_request_info.id)
                    FROM taxi.test_request_info
                    LEFT JOIN portal.users
                    ON test_request_info.user_id = users.id
                    WHERE users.knox_id like %s
                    AND test_request_info.ticket_n like %s
                    AND test_request_info.dateoftrip BETWEEN %s AND %s """
        self.cursor.execute(sql, ('%'+knoxid+'%', '%'+ticket+'%', sdate, edate))
        return self.cursor.fetchone()[0]

    def change_status(self, status, rowid):
        sql = """   UPDATE taxi.test_request_info
                    SET test_request_info.status = %s,
                        test_request_info.admin_comment = NULL
                    WHERE test_request_info.id = %s """
        self.cursor.execute(sql, (status, rowid))
        self.connection.commit()
        return self.connection.close()

    def add_admin_note(self, note, rowid):
        if not note:
            sql = """   UPDATE taxi.test_request_info
                    SET test_request_info.admin_comment = NULL
                    WHERE test_request_info.id = %s """
            self.cursor.execute(sql, (rowid, ))
        else:
            sql = """   UPDATE taxi.test_request_info
                        SET test_request_info.admin_comment = %s
                        WHERE test_request_info.id = %s """
            self.cursor.execute(sql, (note, rowid))
        self.connection.commit()
        return self.connection.close()

    def get_email_data(self, rowid):
        sql = """   SELECT  test_request_info.email,
                            test_request_info.admin_comment
                    FROM taxi.test_request_info
                    WHERE test_request_info.id = %s """
        self.cursor.execute(sql, (rowid, ))
        return self.cursor.fetchone()

    def count_taxi_company(self, knoxid, sdate, edate):
        sql = """   SELECT  test_request_info.taxi_company,
                            COUNT(*) AS Qty,
                            SUM(test_request_info.expance) AS UAH
                    FROM taxi.test_request_info
                    LEFT JOIN portal.users
                    ON test_request_info.user_id = users.id
                    WHERE users.knox_id like %s
                    AND test_request_info.dateoftrip BETWEEN %s AND %s
                    GROUP BY test_request_info.taxi_company """
        self.cursor.execute(sql, ('%'+knoxid+'%', sdate, edate))
        data = self.cursor.fetchall()
        return data

    def count_qty_and_cost_by_user(self, sdate, edate):
        sql = """   SELECT  test_request_info.fullname,
                            SUM(test_request_info.expance) AS UAH
                    FROM taxi.test_request_info
                    WHERE test_request_info.dateoftrip BETWEEN %s AND %s
                    GROUP BY test_request_info.fullname
                    ORDER BY UAH DESC
                    LIMIT 10 """
        self.cursor.execute(sql, (sdate, edate))
        data = self.cursor.fetchall()
        return data

    def count_qty_by_user(self, sdate, edate):
        sql = """   SELECT  test_request_info.fullname,
                            count(*) AS Qty
                    FROM taxi.test_request_info
                    WHERE test_request_info.dateoftrip BETWEEN %s AND %s
                    GROUP BY test_request_info.fullname
                    ORDER BY Qty DESC
                    LIMIT 10 """
        self.cursor.execute(sql, (sdate, edate))
        data = self.cursor.fetchall()
        return data

    def count_all_reasons(self, knoxid, sdate, edate):
        sql = """   SELECT  test_request_info.reason,
                            COUNT(*) AS Qty,
                            SUM(test_request_info.expance) AS UAH
                    FROM taxi.test_request_info
                    LEFT JOIN portal.users
                    ON test_request_info.user_id = users.id
                    WHERE users.knox_id like %s
                    AND test_request_info.dateoftrip BETWEEN %s AND %s
                    GROUP BY test_request_info.reason
                    ORDER BY Qty """
        self.cursor.execute(sql, ('%'+knoxid+'%', sdate, edate))
        data = self.cursor.fetchall()
        return data
