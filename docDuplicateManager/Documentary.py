'''
Created on 17 Jan 2017

@author: achamara

    # Works as a data structure to hold information on individual documentary
    
'''

import os
import hashlib
import json
import sys


class Doc:
    '''
    classdocs
    '''

    video_ext = ['.mp4', '.avi']
    image_ext = ['.jpg', '.bmp', '.gif', '.png']
    text_ext = ['.txt']
    
    reload(sys)  
    sys.setdefaultencoding('utf8')

    def __init__(self, category, name, fqPath, files=[]):
        '''
        Constructor
        '''
        self.category = unicode(category, errors='ignore')
        self.name = unicode(name, errors='ignore')
        self.fqPath = unicode(fqPath, errors='ignore') 
        
        VideoFiles = [ file for file in files if file.endswith((tuple (self.video_ext))) ]
        self.ImageFiles = [ file for file in files if file.endswith((tuple (self.image_ext))) ]
        
        textFileList = [ file for file in files if file.endswith((tuple (self.text_ext))) ]
        self.description = unicode(self.readDescription(textFileList) , errors='ignore')
        
        
        formatedFileList = []
        self.isDuplicate = False
        
        for file in VideoFiles:
            fileObj = {'name': file, 'hash':'', 'duplicate_in': []}
            formatedFileList.append(fileObj)
            
        self.files = formatedFileList
    
        self.fileHashList = []
        
        
        
    def readDescription(self, textFileList):   
        if textFileList == None or len(textFileList) == 0:
            return ""
        
        filePath = os.path.join(self.fqPath, textFileList[0])
        file = open(filePath, "r") 
        text = file.read() 

        return text
        
        
        
    def generateMD5(self):
        
        hashList={}
        
        for file in self.files:
            fqFilePath = os.path.join(self.fqPath, file['name'])
            print("Generating MD5 for file : ", fqFilePath)
            fileHash = self.generateMD5ForFile(fqFilePath)
            file['hash'] = fileHash
            
            print(file['name'] , file['hash'])
            hashList[file['hash']] = fqFilePath
            
            # Check file is duplicate within same directory
            if self.isDuplicate == False and fileHash in self.fileHashList:
                self.isDuplicate = True
                file['duplicate_in'].append({"duplicate_in": fqFilePath})
                
            self.fileHashList.append(file['hash']);
            
        return hashList
    
        
    def generateMD5ForFile(self, fqFileName):
        hash_md5 = hashlib.md5()
        with open(fqFileName, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def __str__(self):
        return (self.name)
    
    def getJSONObject(self):

        jsonText = json.dumps({'name': self.name, 'category': self.category, 'description': self.description , 'fq_path': self.fqPath , 'cover_image': self.ImageFiles , 'duplicate_found': self.isDuplicate, 'file_hash' : self.fileHashList , 'files':  [] }) 
    
        jsonObject = json.loads(jsonText)
        
        for file in self.files:
            jsonObject["files"].append({"file": file})
    
        return jsonObject
