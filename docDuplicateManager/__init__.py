from GenerateData  import DocManager


def main():
        
    docManager = DocManager()
    
    docManager.initConfigData()
    
    docManager.populateDocumentaryList()

    docManager.init()

    docManager.insertToDB()

    docManager.startHTTPServer()

        
if  __name__ == '__main__':
    main()
