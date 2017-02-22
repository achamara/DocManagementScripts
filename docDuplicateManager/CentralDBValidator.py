'''
Created on 9 Feb 2017

@author: achamara
'''

import sqlite3 as lite
import sys
import os

import time
import datetime


class DBValidator:
    '''
    classdocs
    '''

    con = None
    
    
    def findMatchingDoc(self, dbLocation, doc):
        con = lite.connect(dbLocation)
        
        with con:
            
            try:
                cur = con.cursor()  
                cur.execute('SELECT * FROM Doc WHERE name="{name}"'.format(name=doc.name))
                id_exists = cur.fetchone()
                if id_exists:
                    print('Duplicate Doc : {0} '.format(id_exists))
                    return True
                else:
                    return False
            except lite.OperationalError, e:
                print ("Table Doc not found, ignoring..")
                return False

            
    def findMatchingDocFiles(self, doc):
        con = lite.connect(dbLocation)
        
        with con:
            
            try:
                cur = con.cursor()  
                # cur.execute('SELECT * FROM File WHERE fileHash in ({name})'.format(name=doc.name))
                result_set = cur.execute('SELECT * FROM File WHERE fileHash in (%s)' % ("?," * len(doc.fileHashList))[:-1], doc.fileHashList)

                for result in result_set:
                    print result
                    
            except lite.OperationalError, e:
                print ("Table File not found, ignoring..")
                return False
                        
        # return self.dbValidator.findMatchingDocFiles(self.centralDBLocation, doc.fileHashList)   
    
    
    def insertNewDoc(self, dbLocation, docInfo):
        # try:
        con = lite.connect(dbLocation)
            
        with con:
            cur = con.cursor()    
            cur.execute("CREATE TABLE IF NOT EXISTS Doc(id INTEGER PRIMARY  KEY, name TEXT(150), category TEXT(50), fqPath TEXT(500), ts TEXT(50) )")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_doc_name on Doc (name) ")
            
            cur.execute("CREATE TABLE IF NOT EXISTS File(id INTEGER PRIMARY  KEY, name TEXT(150), docId INTEGER, fileHash TEXT(50) , FOREIGN KEY(docId) REFERENCES Doc(id) )")


            try:
                cur.execute("INSERT INTO Doc( id, name,category,fqPath, ts)  VALUES(NULL, ? , ? , ? ,  ?)", (str(docInfo.name).encode('utf8') , docInfo.category, str(docInfo.fqPath).encode('utf8'), datetime.datetime.utcnow()))
                lastId = cur.lastrowid 
                print ("The Doc Id of the inserted row is %d" % lastId)
                
                fileIds = []
                
                print ("Total of {0} files were found, trying to insert to File table.".format( len(docInfo.files)) )

                for file in docInfo.files:
                    print("Inserting {0} .. ".format(file['name']))
                    fileIndex = cur.execute("INSERT INTO File( id, name, docId ,fileHash)  VALUES(NULL,  ? , ? ,  ?)", ( u"'"+file['name']+"'" , lastId , file['hash']))
                    fileIds.append(fileIndex)
                    
                if len(docInfo.files) is len(fileIds):
                    print ("INFO : Total of {0} files were inserted under the Doc {1} ".format(len(fileIds), docInfo.name))
                else:
                    print ("WARNNING : Only {0} files were inserted under the Doc {1} ".format(len(fileIds), docInfo.name))
                    
            except lite.IntegrityError, e:
                print ("WARNNING : Duplicate Doc found, {0} ".format(docInfo.name))
            

        # except lite.Error, e:
            # print ("# CONFIG ERROR :: Error while connecting to the DB :  %s:" % e.args[0])
            # return False
    
    
    def validateDBConnection(self, dbLocation):
        try:
            con = lite.connect(dbLocation)
            
            cur = con.cursor()    
            cur.execute('SELECT SQLITE_VERSION()')
            
            data = cur.fetchone()
            print ("# CONFIG :: SQLite DB version: %s " % data)   
            
            if not os.path.isfile(dbLocation):
                print ("# CONFIG ERROR :: Error while locating the DB file :  %s:" % dbLocation)
                return False

           
        except lite.Error, e:
            
            print ("# CONFIG ERROR :: Error while connecting to the DB :  %s:" % e.args[0])
            return False
            
        finally:
            if con:
                con.close()
            
        return True    
            
            
    # def __init__(self, params):
        '''
        Constructor
        '''
        
