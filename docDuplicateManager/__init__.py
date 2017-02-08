from GenerateData  import DocManager


def main():
        
    print ("Starting DocDulicateManager 1.0")
    
    docManager = DocManager()
    
    docManager.initConfigData()
    
    docManager.populateDocumentaryList()

    docManager.init()

    docManager.insertToDB()

    docManager.startHTTPServer()

    print ("\n Exiting DocDulicateManager 1.0")
        
if  __name__ == '__main__':
    main()
