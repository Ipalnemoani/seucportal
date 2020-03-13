# -*- coding: utf-8 -*-

import json


from app import app
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3 import ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, SCHEMA
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError, LDAPSocketReceiveError


class LDAPLogin():
    
    def __init__(self):
        self.USERNAME = None
        self.AD_PASSWORD = None
        self.AD_USER = None
        self.AD_PORT = app.config['CORP_AD_PORT']
        self.AD_SERVER = app.config['CORP_AD_SERVER']
        self.AD_SEARCH_TREE = app.config['CORP_AD_SEARCH_TREE']
        self.AD_CONN_TOUT = app.config['CORP_AD_CONN_TIMEOUT']
        self.CORP_AD_HOST = app.config['CORP_AD_HOST']

        self.conn = None
        self.MSGINFO = None
        self.employee = None
        
    def conn_to_ad(self, username, password):
        try:
            self.USERNAME = username
            self.AD_PASSWORD = password
            self.AD_USER = self.USERNAME+self.CORP_AD_HOST

            self.server = Server(self.AD_SERVER, get_info=SCHEMA, port = self.AD_PORT, connect_timeout=self.AD_CONN_TOUT)
            self.conn = Connection( self.server, user=self.AD_USER, 
                                    password=self.AD_PASSWORD, auto_bind=True, 
                                    read_only=True)
            self.MSGINFO = 'Successfully Login!'
            return True
        except LDAPBindError:
            self.MSGINFO = 'Invalid Login or Password!\nPlease, try again!'
            return False
        except (LDAPSocketOpenError, LDAPSocketReceiveError):
            self.MSGINFO = 'AD Server is unavailable!\nPlease, contact to system administrator!'
            return False


    def find_employee_data(self):
        self.conn.search(self.AD_SEARCH_TREE,
                        '(&(objectCategory=Person)(sAMAccountName={0}))'.format(self.USERNAME), 
                        SUBTREE,
                        attributes =['cn', 'proxyAddresses', 'department',
                                    'sAMAccountName', 'displayName', 'telephoneNumber', 
                                    'ipPhone', 'streetAddress', 'title',
                                    'manager', 'objectGUID', 'company',
                                    'lastLogon', 'homeDirectory', 'distinguishedName', 'mail',
                                    'mobile', 'description', 'employeeNumber'])
        return json.loads(self.conn.entries[0].entry_to_json())["attributes"]
    

if __name__ == '__main__':
    ldapserv = LDAPLogin()
    ldapserv.conn_to_ad('lysenko.v', 'Samsung01')
    if ldapserv.conn_to_ad():
        user = ldapserv.find_employee_data()
        print(user)
    else:
        print(ldapserv.MSGINFO)



