from collections import OrderedDict
import sys


def loadDataElector(path, max_len):
    """
    This function receive the path and try to convert to a sql file.
    :param path: This is the file .txt
    :param max_len: This is the round of the values creation
    :return: The result is the creation of the querys.sql, and contain the Elector querys to insert data.
    """
    count = 0
    txtFile = ""
    try:
        print("Loading " + path + " in loadData")
        txtFile = open(path)
    except:
        print("Can't read this path..")
        return

    #this file save the total lines in .txt file
    linesList = txtFile.readlines()
    #the temporal tupleList. When count older than max_len, it saves the values, inserts them into the .sql file
    # and then resets the values
    tupleList = []

    for line in linesList:
        tupleToSave = splitLine(line)
        tupleList.append(tupleToSave)
        if (count > max_len):
            #create a list of tuples with de values format in sql
            tupleListValues = createTupleListValues(tupleList)
            #save the lines into a .sql file
            saveLine(tupleListValues)
            tupleList = []
            count = 0
        count += 1
    print("Success")


def createTupleListValues(tupleList):
    """
    This function converts to tuple when you pass a dictionary, is used to format field to append in sql
    values
    :param tupleList: This is the tuple list created in the previous function, the len of this tuple depends to the max_len value
    :return:A tuple string with all the values to insert
    """
    tupleString = ""
    for element in tupleList:
        # this validation is because mysql does not recognize a comma at the end of the values
        if (tupleList[-1] == element):
            tupleString += "%s " % str(element)
        else:
            tupleString += "%s, " % str(element)
    return tupleString


def saveLine(values):
    """
     This function get the values in the params and try to append in querys.sql file
     :param values: This is the values to insert function in sql
     """
    sql = "INSERT INTO %s (idCard, gender, cad_date, board, fullName, codelec_id) VALUES %s;" % (
        'padronelectoral_elector', values)
    sqlFile = open("querysElector.sql", "a")
    sqlFile.write(sql)

def splitLine(line):
    """
    This function convert each line in the .txt file in a tuple.
    :param line: Each line in the .txt file
    :return: Line converted in a tuple
    """
    split = line.split(",")
    try:
        fullName = "%s %s %s" % (split[5].strip(), split[6].strip(), split[7].strip())
    except:
        print("ERROR ", split)
        raise
    # this is the order: (idCard, gender, cad_date, board, fullName, codelec_id)
    splitTuple = (split[0], split[2], split[3], split[4], fullName, split[1])

    return splitTuple

#this temporal variables are to save the current provinceid and cantonid, because
#because otherwise the function save in the .sql file many times in the same call
provinceIdAux = 0
cantonIdAux = 0
def splitLineCodelec(line):
    """
    Receive each line in the .txt file and try to append
    :param line: Each line in the .txt file
    :return: Each line is saved in its corresponding file
    """
    global provinceIdAux
    global cantonIdAux
    split = line.split(",")
    codelec = split[0]

    provinceData = (codelec[0], split[1])
    cantonData =  (codelec[1:3],str(split[2]),codelec[0] )
    districtData = (codelec,(split[3].strip()),codelec[1:3])

    #this if is needed because in case that not exist, the file will append repeat data many times
    if(provinceIdAux!=codelec[0]):
        orderValuesProvince = "code, name"
        queryProvince = createQuerys(orderValuesProvince, 'padronelectoral_province', provinceData)
        sqlFileP = open("querysProvince.sql", "a")
        sqlFileP.write(queryProvince)
        provinceIdAux = codelec[0]

    # this if is needed because in case that not exist, the file will append repeat data many times
    if(cantonIdAux!=codelec[1:3]):
        orderValuesCanton = "code, name,province_id"
        queryCanton = createQuerys(orderValuesCanton, 'padronelectoral_canton', cantonData)
        sqlFileC = open("querysCanton.sql", "a")
        sqlFileC.write(queryCanton)
        cantonIdAux = codelec[1:3]

    orderValuesDistrict = "codelec, name, canton_id"
    queryDistrict = createQuerys(orderValuesDistrict, 'padronelectoral_district', districtData)
    sqlFileD = open("querysDistrict.sql", "a")
    sqlFileD.write(queryDistrict)

def createQuerys(values, tableName, valuesTuple):
    """
    :param values: The values order in each insert
    :param table: The table name
    :param valuesTuple: The values that read in the .txt file after being converted to tuple
    :return: The string created, that it will be save in the corresponding .sql file
    """
    return "Insert Into %s (%s) Values %s;" % (tableName, values, valuesTuple)

def loadDataCodelec(path):
    """
    This function is to create all the .sql files (province, canton and distric)
    :param path: Receive the .txt file url
    :return: All the .sql files (province, canton and distric)
    """
    txtFile = ""
    try:
        print("Loading "+path)
        txtFile = open(path)

    except:
        print("Can't read this path..")
        return
    linesList = txtFile.readlines()
    for line in linesList:
        splitLineCodelec(line)


def defineParameters(pathDistelec, path):
    """
    #receive the codelec and padron_electoral paths in the parameters in the first call
    :param pathDistelec: Path distelec .txt url
    :param path:  Padron_electoral .txt url
    """
    if len(sys.argv) < 3:
        print("Help:  python loadData.py <diselect path>  <registry path>")
        return
    loadDataElector(path, 100000)
    loadDataCodelec(pathDistelec)

#receive the codelec and padron_electoral paths in the parameters in the first call
defineParameters(sys.argv[1], sys.argv[2])

#/home/miguelmendezrojas/Descargas/padron_completo/Distelec.txt
#/home/miguelmendezrojas/Descargas/padron_completo/PADRON_COMPLETO.txt
