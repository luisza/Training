from collections import OrderedDict
import sys


def loadDataElector(path, max_len):
    """
    This function receive the path and try to convert to a sql file.
    :param path:
    :param max_len:
    :return:
    """
    count = 0
    txtFile = ""
    try:
        print("Loading " + path + " in loadData")
        txtFile = open(path,encoding="ISO-8859-1")
    except:
        print("Can't read this path..")
        return

    linesList = txtFile.readlines()
    tupleList = []

    for line in linesList:
        tupleToSave = splitLine(line)
        tupleList.append(tupleToSave)
        if (count > max_len):
            #create a list of tuples with de values format in sql
            tupleListValues = createTupleListValues(tupleList)
            saveLine(tupleListValues)
            tupleList = []
            count = 0
        count += 1

    print("Success")


def createTupleListValues(tupleList):
    """
    This function converts to tuple when you pass a dictionary, is used to format field to append in sql
    values
    :param dictionaryList:
    :return:
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
    sql = "INSERT INTO %s (idCard, gender, cad_date, board, fullName, codelec_id) VALUES %s;" % (
        'padronelectoral_elector', values)
    sqlFile = open("querys.sql", "a")
    sqlFile.write(sql)

def splitLine(line):
    split = line.split(",")
    try:
        fullName = "%s %s %s" % (split[5].strip(), split[6].strip(), split[7].strip())
    except:
        print("ERROR ", split)
        raise
    # this is the order: (idCard, gender, cad_date, board, fullName, codelec_id)
    splitTuple = (split[0], split[2], split[3], split[4], fullName, split[1])

    return splitTuple


provinceIdAux = 0
cantonIdAux = 0
def splitLineCodelec(line):
    global provinceIdAux
    global cantonIdAux
    split = line.split(",")
    codelec = split[0]

    provinceData = (codelec[0], split[1])
    cantonData =  (codelec[0]+codelec[1:3],str(split[2]),codelec[0] )
    districtData = (codelec,(split[3].strip()),codelec[0]+codelec[1:3])

    #this if is needed because in case that not exist, the file will append repeat data many times
    if(provinceIdAux!=codelec[0]):
        orderValuesProvince = "code, name"
        queryProvince = createQuerys(orderValuesProvince, 'padronelectoral_province', provinceData)
        sqlFileP = open("querysProvince.sql", "a")
        sqlFileP.write(queryProvince)
        provinceIdAux = codelec[0]

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

def createQuerys(values, table, valuesTuple):
    return "Insert Into %s (%s) Values %s;" % (table, values, valuesTuple)

def loadDataCodelec(path):
    txtFile = ""
    try:
        print("Loading "+path)
        txtFile = open(path,encoding="ISO-8859-1")

    except:
        print("Can't read this path..")
        return
    linesList = txtFile.readlines()
    for line in linesList:
        splitLineCodelec(line)


def defineParameters(pathDistelec, path):
    if len(sys.argv) < 3:
        print("Help:  python loadData.py <diselect path>  <registry path>")
        return
    loadDataElector(path, 1000)

    loadDataCodelec(pathDistelec)

defineParameters(sys.argv[1], sys.argv[2])

#/home/miguelmendezrojas/Descargas/padron_completo/Distelec.txt
#/home/miguelmendezrojas/Descargas/padron_completo/PADRON_COMPLETO.txt
