# -*- coding: utf-8 -*-

import json
import pymysql.cursors
import pymysql.err
import mysql.connector


from app import app


from pymysql.err import OperationalError, InternalError
from mysql.connector import errorcode
from datetime import datetime, timedelta


class SEUCPortalDB():
    
    def __init__(self, dbname):
        self.user = app.config['DB_USER']
        self.password = app.config['DB_PASSWORD']
        self.host = app.config['DB_HOST']
        self.port = app.config['DB_PORT']
        self.dbname = dbname
        self.cursor = None
        self.connection = None
        self.DBMSGINFO = None

    def connect_to_db(self):
        try:
            self.connection = pymysql.connect(
                                                user=self.user,
                                                password=self.password,
                                                host=self.host,
                                                port=int(self.port),
                                                database=self.dbname
                                                )
        except OperationalError as err:
            if err.args[0] == 1054:
                self.DBMSGINFO = "DataBase Access Denied! Invalid Login or Password! Please, contact to system administrator!"
                return False
            elif err.args[0] == 2003:
                self.DBMSGINFO = "Can't connect to MySQL server! Please, contact to system administrator!"
                return False
            else:
                self.DBMSGINFO = "DataBase Unknown Error [{}]! Please, contact to system administrator!".format(err.args[0])
                return False
        except InternalError as err:
            if err.args[0] == 1049:
                self.DBMSGINFO = "DataBase does not exist! Please, contact to system administrator!"
                return False
            else:
                self.DBMSGINFO = "DataBase Unknown Error [{}]! Please, contact to system administrator!".format(err.args[0])
                return False
        else:
            self.cursor = self.connection.cursor()
            return True

    def get_emplid_by_knox(self, knoxid, usermail):
        sql = """   SELECT users.id 
                    FROM portal.users 
                    WHERE users.knox_id = %s OR users.email = %s """
        self.cursor.execute(sql, (knoxid, usermail))
        id = self.cursor.fetchone()
        if id:
            return id[0]
        else:
            return None

    def insert_empl_info(self, *data):
        sql = """   INSERT INTO portal.users (users.knox_id, users.email,
                                            users.full_name, users.gencode,
                                            users.department) 
                    VALUES(%s, %s, %s, %s, %s) """
        self.cursor.execute(sql, data)
        self.connection.commit()
        row_id = self.cursor.lastrowid
        return row_id

    def get_change_work_date(self, empl_id):
        sql = """   SELECT DATE(dateof_change)
                    FROM  work_schedule
                    WHERE user_id = %s """
        self.cursor.execute(sql, (empl_id, ))
        return self.cursor.fetchone()[0]

    def select_user_info(self, emplid):
        loginday = datetime.now().date()
        wdate = self.get_change_work_date(emplid)
        if loginday < wdate:
            tstart = 'time_start'
            tend = 'time_end'
        else:
            tstart = 'change_time_start'
            tend = 'change_time_end'

        sql = """   SELECT users.email, 
                        users.department, 
                        users.division,
                        CONCAT(TIME_FORMAT(work_schedule.{0}, '%H:%i:%S'), 
                                '-',  
                                TIME_FORMAT(work_schedule.{1}, '%H:%i:%S')) AS worktime
                    FROM portal.users, portal.work_schedule 
                    WHERE users.id = %s
                    AND users.status = 1 AND users.id = work_schedule.user_id""".format(tstart, tend)

        self.cursor.execute(sql, (emplid, ))

        headers = [key[0].capitalize() for key in self.cursor.description]
        data = [i for i in self.cursor.fetchone()]
        items = {headers[i]:data[i] for i in range(len(headers))}
        
        return json.dumps(items)

    def if_admin(self, knox_id):
        sql = """   SELECT users.admin
                    FROM portal.users
                    WHERE users.knox_id = %s """
        self.cursor.execute(sql, (knox_id, ))
        admin = self.cursor.fetchone()[0]
        self.connection.close()
        return admin

    def close_connection(self):
        return self.connection.close()


if __name__ == '__main__':
    db = SEUCPortalDB('taxi')
    db.connect_to_db()
