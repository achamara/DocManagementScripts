'''
Created on 17 Jan 2017

@author: achamara

    # Read the main dir. & traverse through each category & valid files
    # Generate MD5 on file content and insert into the DB (JSON File).
    
'''


import sys
from tinydb import TinyDB, Query, where
import  ConfigParser, os
import datetime
import time
import zipfile

from HandlerImpl import RequestHandler
from Documentary import Doc
import SocketServer

class DocManager:
    
    fqPath = ""
    port = 8282
    dbFileName = 'db.json'
    dbTableName = ''
    
    docFolderName = ''
    resLocation = '.res/config.js'
    
    videoExt = []
    imageExt = []
    textExt = []
    
    categoryList = []
    documentaryList = []
    config = ConfigParser.ConfigParser()
    
    # Load the config. setting from the provided file
    def loadConfigSettings(self):
        self.fqPath = self.config.get('Folder_Location', 'doc_location')
        print ("# CONFIG :: Doc Folder to read  = " + self.fqPath)
        
        
        self.docFolderName = os.path.basename(self.fqPath)
        
        port = self.config.get('HTTP_Settings', 'port')
        self.port = int(port)
        print ("# CONFIG :: HTTP server port  = " + port)
        
        self.dbFileName = self.config.get('DB_Details', 'json_db_file_name')
        print ("# CONFIG :: JSON DB file name  = " + self.dbFileName)      
        
        self.dbTableName = self.config.get('DB_Details', 'json_db_table_name')
        print ("# CONFIG :: JSON DB table name = " + self.dbTableName)   
        
        videoExt = self.config.get('File_Types', 'video_ext')
        self.videoExt = videoExt.split(',')
        print ("# CONFIG :: Video file types  = " + videoExt)
        
        imageExt = self.config.get('File_Types', 'image_ext')
        self.imageExt = imageExt.split(',')
        print ("# CONFIG :: Image file types  = " + imageExt)      
        
        textExt = self.config.get('File_Types', 'text_ext')
        self.textExt = textExt.split(',')
        print ("# CONFIG :: Text file types = " + textExt)   
    
    
    
    
    # Check for the config. file is provided as a parameter
    def initConfigData(self):
        if len(sys.argv) >= 2:
            if os.path.isfile(sys.argv[1]):
                print ("Reading configuration file from : " + sys.argv[1])
                self.config.readfp(open(sys.argv[1]))
        else:
            print("Configuration file path is not provided, exiting!")
            exit()    
        
        self.loadConfigSettings()
        
        
    def writeDBPath(self):
        
        resLocation = os.path.join(self.fqPath, self.resLocation)
        
        file = open(resLocation, "w") 
 
        textToWrite = "var config_data = { db_file_path : '###DB_PATH###', file_title : '###TITLE###' };"
        
        file.write(textToWrite.replace('###DB_PATH###' , self.dbName).replace('###TITLE###' , self.docFolderName)) 
        
        file.close() 
    
    # init json db.
    def initJSON_DB(self):
        ts = time.time()
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%d_%m_%Y %H_%M_%S')
        
        self.dbName = self.dbFileName + '_' + timeStamp + '.json'
        
        
        
        dbPath = os.path.join(self.fqPath, self.dbName)
        self.db = TinyDB(dbPath)
        self.table = self.db.table(self.dbTableName)
    
    
    def extractResourceFile(self):
        mydir = os.path.dirname(os.path.abspath(__file__))
        zipFilePath = os.path.join(mydir, 'res_1.0.zip')
        #zipFilePath = '/'.join('res_1.0.zip') 
        print (zipFilePath)
        zip_ref = zipfile.ZipFile(zipFilePath, 'r')
        zip_ref.extractall(self.fqPath)
        zip_ref.close()



    def configureHTTPRequest(self):
        customPath = (
            # [url_prefix ,  directory_path]
            ['/files', self.fqPath],
            ['', self.fqPath]
            ) 
        RequestHandler.changeRootFolder(customPath)
        
        self.extractResourceFile()
        self.writeDBPath()

    
    # init method.
    def init(self):
        self.initConfigData()
        self.initJSON_DB()
        self.configureHTTPRequest()
    
    
    # iterate the given path and add files to a list.
    def populateDocumentaryList(self):
        
        for (dirpath, dirnames, filenames) in os.walk(self.fqPath):
        
            relativePath = dirpath.replace(self.fqPath, "")
            
            if len(relativePath) == 0:
                continue
            
            pathArray = relativePath.split(os.path.sep)
            
            # length = 2 then main category, length = 3 then corresponding doc.
            if len(pathArray) == 2 :
                print ("Category found : " + pathArray[1])
                self.categoryList.extend(filenames)
            elif len(pathArray) == 3 :
                print ("Doc. found : " + pathArray[2])
                doc = Doc(pathArray[1], pathArray[2], dirpath , filenames)
                self.documentaryList.append(doc)
                # print (filenames)
    
    
    # Add files to db.
    def insertToDB(self):
        for doc in self.documentaryList:
            print(doc.generateMD5())
            
            if doc.isDuplicate == False and self.findDuplicatesInDB(doc) == True:
                doc.isDuplicate = True
                
            self.table.insert(doc.getJSONObject())
            
            
    # Find duplicate entries for a file   
    def findDuplicatesInDB(self, doc):
        Docu = Query()
        
        for file in doc.files:
            hashCount = self.table.count(Docu.file_hash.any (file['hash']));
        
            if hashCount > 0: 
                return True 
        
        return False
    
    # Start local HTTP server
    def startHTTPServer(self):
        httpd = SocketServer.TCPServer(("", self.port), RequestHandler)
        print ("Local HTTP server is serving at port : ", self.port)
        httpd.serve_forever()
    
    


    
    
    

