from GenerateData  import DocManager


def main():
        
    print ("Starting DocDulicateManager 1.0\n")
    
    docManager = DocManager()
    
    docManager.initConfigData()
    
    if not docManager.isWebserviceRequest():
        docManager.populateDocumentaryList()
    
        docManager.init()
    
        docManager.insertToDB()
    
        docManager.startHTTPServer()

    print ("\nExiting DocDulicateManager 1.0")
        
if  __name__ == '__main__':
    main()
    
