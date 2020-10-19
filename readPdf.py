import PyPDF2
import sys

fileName = sys.argv[1]

def read_and_write_pdf(fileName):
    keys = ["publish", "produc", "test", "launch",
        "help", "research", "advice", "gather", "guidance", "monetary", "inquir", "resolut"]
    fileNameFull = fileName + '.pdf'
    pdfFileObj = open(fileNameFull, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pageNum = pdfReader.numPages
    text = []
    for i in range(pageNum):
        pageObj = pdfReader.getPage(i)
        text.append(pageObj.extractText())
    
    key_sts = []
    for t in text:
        sts = t.replace('\n', '').replace('No. ','No.').replace('Nos. ', 'Nos.').split('. ')
        for s in sts:
            for k in keys:
                if k in s.lower():
                    key_sts.append(s)
    txtFileName = fileName + '.txt'
    with open(txtFileName, 'w') as f:
        for item in key_sts:
            f.write("%s\n" % item)


read_and_write_pdf(fileName)
