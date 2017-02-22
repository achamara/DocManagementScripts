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

from CentralDBValidator import DBValidator

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
    
    ignoreFolderNames = []
    
    
    fileMap = {}
    
    
    resZipName = 'res_1.0.zip'
    
    dbValidator = DBValidator ()
    
    isWebRequest = True
    
    paraMessage = "Please use the below settings to run the Duplicate manager service. \n # --config <configuration file path ending in .ini>  - provide the location of the ini files containig the configuration info. \n # --ser <port address>    - indication to start the web server under the specified port."
    
    
    # Load the config. setting from the provided file
    def loadConfigSettings(self):
        self.fqPath = self.config.get('Folder_Location', 'doc_location')
        print ("# CONFIG :: Doc Folder to read  = " + self.fqPath)
        
        self.resZipName = self.config.get('Folder_Location', 'res_zip_name')
        print ("# CONFIG :: Resource ZIP file name  = " + self.resZipName)
        
        
        self.docFolderName = os.path.basename(self.fqPath)
        
        port = self.config.get('HTTP_Settings', 'port')
        self.port = int(port)
        print ("# CONFIG :: HTTP server port  = " + port)
        
        self.dbFileName = self.config.get('DB_Details', 'json_db_file_name')
        print ("# CONFIG :: JSON DB file name  = " + self.dbFileName)      
        
        self.dbTableName = self.config.get('DB_Details', 'json_db_table_name')
        print ("# CONFIG :: JSON DB table name = " + self.dbTableName)   
        
        
        self.centralDBLocation = self.config.get('DB_Details', 'central_sqllite_db_path')
        print ("# CONFIG :: Central SQLite DB path  = " + self.centralDBLocation)
        
        self.addToCentralDB = self.config.get('DB_Details', 'insert_to_central_db')
        print ("# CONFIG :: Add new doc's to Central SQLite DB = " + self.addToCentralDB)
        
        
        videoExt = self.config.get('File_Types', 'video_ext')
        self.videoExt = videoExt.split(',')
        print ("# CONFIG :: Video file types  = " + videoExt)
        
        imageExt = self.config.get('File_Types', 'image_ext')
        self.imageExt = imageExt.split(',')
        print ("# CONFIG :: Image file types  = " + imageExt)      
        
        textExt = self.config.get('File_Types', 'text_ext')
        self.textExt = textExt.split(',')
        print ("# CONFIG :: Text file types = " + textExt)   
    
        ignoreFolderNames = self.config.get('Ignore_List', 'folder_name')
        self.ignoreFolderNames = ignoreFolderNames.replace(' ', '').split(',')
        print ("# CONFIG :: Folder names to ignore = " + ignoreFolderNames)   
    
    
    # Check for the config. file is provided as a parameter
    
    def initConfigData(self):
        if len(sys.argv) >= 2:
            if sys.argv[1] == "--config"  and os.path.isfile(sys.argv[2]):
                print ("Reading configuration file from : " + sys.argv[2])
                self.config.readfp(open(sys.argv[2]))
                self.loadConfigSettings()
                self.isWebRequest = False
            elif sys.argv[1] == "--ser"  and sys.argv[2].isdigit():
                print ("Trying to start the web server on port {1} on location : {1} ".format(sys.argv[2], sys.argv[3]))
                self.isWebRequest = True
                if not self.configureHTTPRequest(str(sys.argv[3])) is False:
                    self.startHTTPServer(int(sys.argv[2]))
            else:
                print(self.paraMessage)
        else:
            print(self.paraMessage)
            exit()    
        
        
    def isWebserviceRequest(self):
        return self.isWebRequest;
                
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
        zipFilePath = os.path.join(mydir, self.resZipName)
        # zipFilePath = '/'.join('res_1.0.zip') 
        print (zipFilePath)
        zip_ref = zipfile.ZipFile(zipFilePath, 'r')
        zip_ref.extractall(self.fqPath)
        zip_ref.close()



    def configureHTTPRequest(self, argPath=None):
        if argPath is not None:
            self.fqPath = argPath
        customPath = (
            # [url_prefix ,  directory_path]
            ['/files', self.fqPath],
            ['', self.fqPath]
            )
        
        if os.path.isdir(self.fqPath):
            RequestHandler.changeRootFolder(customPath)
        else:
            print("Provided folder path is invalid : "+ self.fqPath)
            return False 

        
        
        if argPath is None:
            self.extractResourceFile()
            self.writeDBPath()

    
    # init method.
    def init(self):
        self.initConfigData()
        self.initJSON_DB()
        self.initCentralDB()
        self.configureHTTPRequest()
    
    
    def initCentralDB(self):
        
        self.isCentralDBConfigured = self.dbValidator.validateDBConnection(self.centralDBLocation)
        
        if self.isCentralDBConfigured is False:
            print("# CONFIG :: Central DB connection error, validation will be ignored. ")
        
    
    def inIgrnoeList(self, dirName):
        if dirName in self.ignoreFolderNames:
            return True;
        else:
            return False;
        
        
    # iterate the given path and add files to a list.
    def populateDocumentaryList(self):
        
        for (dirpath, dirnames, filenames) in os.walk(self.fqPath):
        
            relativePath = dirpath.replace(self.fqPath, "")
            
            if len(relativePath) == 0 :
                print ("Folder ignored : " + relativePath)
                continue
            
            pathArray = relativePath.split(os.path.sep)
            
            # length = 2 then main category, length = 3 then corresponding doc.
            if len(pathArray) == 2 and not self.inIgrnoeList(pathArray[1]):
                print ("Category found : " + pathArray[1])
                self.categoryList.extend(filenames)
            elif len(pathArray) == 3 and not self.inIgrnoeList(pathArray[2]):
                print ("Doc. found : " + pathArray[2])
                doc = Doc(pathArray[1], pathArray[2], dirpath , filenames)
                self.documentaryList.append(doc)
                
                
                # print (filenames)
    
    
    # Add files to db.
    def insertToDB(self):
        for doc in self.documentaryList:

            if doc.isDuplicate == False and self.findDuplicates(doc) == True:
                doc.isDuplicate = True
                
            self.table.insert(doc.getJSONObject())
            
            if(self.centralDBLocation is not None and bool(self.addToCentralDB) is True and doc.isDuplicate is False):
                print("Inserting the Doc : {0} to central DB.".format(doc.name))
                self.dbValidator.insertNewDoc(self.centralDBLocation, doc)
          
          
          
    def findDuplicateDocs(self, doc):
        return self.dbValidator.findMatchingDoc(self.centralDBLocation, doc)  
  
            
    def findDuplicateFiles(self, doc):
        return self.dbValidator.findMatchingDocFiles(self.centralDBLocation, doc.fileHashList)   
    
    
    def findDuplicateFilesInCurrentDir(self, doc):
        
        fileHashMap = doc.generateMD5();
        
        print("Folder : {0} , contains {1} files, start duplicate validation..".format(doc.name, len(fileHashMap.keys())))
        
        for hash, fqPath in fileHashMap.items():
            print("File : {0}, Hash : {1}".format(fqPath, hash))
            tmpList = []
             
            if hash in  list(self.fileMap.keys()):
                doc.isDuplicate = True
                tmpList = self.fileMap.get(hash)
                tmpList.append(fqPath)
                self.fileMap[hash] = tmpList
                return True
             
            tmpList.append(fqPath)
            self.fileMap[hash] = tmpList
            
        
            
    # Find duplicate entries for a file in
    #  a. Current Archive
    #  b. Central location
    def findDuplicates(self, doc):
        
        return self.findDuplicateFilesInCurrentDir(doc) or self.findDuplicateDocs(doc)
        # a. find duplicates in Current Archive
        
            
            
# b. find duplicates in  Central location
        

        # Docu = Query()
        
        # for file in doc.files:
            # hashCount = self.table.count(Docu.file_hash.any (file['hash']));
        
            # if hashCount > 0: 
                # return True 
        
        # return False
    
    # Start local HTTP server
    def startHTTPServer(self, customPort=None):
        if customPort is not None:
            self.port = customPort
        try:
            httpd = SocketServer.TCPServer(("", self.port), RequestHandler)
            print ("Local HTTP server is serving at port : ", self.port)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Shouting Down the HTTP server...")
            pass
    


    
    
    

