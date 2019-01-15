def loadData(path, max_len):
    count = 0
    txtFile = ""
    try:
        txtFile = open(path)
    except:
        print("Can't read this path..")
        return

    linesList = txtFile.readlines()
    dictionaryList = []

    for line in linesList:
        dictionaryToSave = splitLine(line)
        dictionaryList.append(dictionaryToSave)
        if (count > max_len):
            tuple = dictionaryListToValues(dictionaryList)
            saveLine(tuple)
            dictionaryList = []
            count = 0
        count += 1

    print("Success")


def dictionaryListToValues(dictionaryList):
    tupleList = [tuple(element.values()) for element in dictionaryList]
    tupleString = ""
    for element in tupleList:
        # this validation is because mysql does not recognize a comma at the end of the values
        if (tupleList[-1] == element):
            tupleString += "%s " % str(element)
        else:
            tupleString += "%s, " % str(element)
    return tupleString


def saveLine(values):
    sql = "INSERT INTO %s (idCard, gender, cad_date, board, fullName, name, lastname1, lastname2, codelec_id) VALUES %s;" % (
        'padronelectoral_elector', values)
    sqlFile = open("querys.sql", "a")
    sqlFile.write(sql)

def splitLine(line):
    split = line.split(",")
    fullName = "%s %s %s" % (split[5].strip(), split[6].strip(), split[7].strip())
    orderedInfo = {
        'idCard': split[0],
        'gender': split[2],
        'cad_date': split[3],
        'board': split[4],
        'fullName': fullName,
        'name': split[5].strip(),
        'lastname1': split[6].strip(),
        'lastname2': split[7].strip(),
        'codelec': split[1]
    }
    return orderedInfo

provinceIdAux = 0
cantonIdAux = 0
def splitLineCodelec(line):
    global provinceIdAux
    global cantonIdAux
    split = line.split(",")
    codelec = split[0]
    provinceData = {'id': codelec[0],
                   'name':split[1]}
    cantonData = {'id': codelec[1:3],
                  'name': split[2],
                  'province': codelec[0]}
    districtData = {'id': codelec[3:],
                    'codelec': codelec,
                    'name': split[3].strip(),
                    'canton': codelec[1:3]}

    #this if is needed because in case that not exist, the file will append repeat data many times
    if(provinceIdAux!=codelec[0]):
        queryProvince = createQuerys('padronelectoral_province', provinceData)
        sqlFileP = open("querysProvince.sql", "a")
        sqlFileP.write(queryProvince)
        provinceIdAux = codelec[0]

    if(cantonIdAux!=codelec[1:3]):
        queryCanton = createQuerys('padronelectoral_canton', cantonData)
        sqlFileC = open("querysCanton.sql", "a")
        sqlFileC.write(queryCanton)
        cantonIdAux = codelec[1:3]

    queryDistrict = createQuerys('padronelectoral_district', districtData)
    sqlFileD = open("querysDistrict.sql", "a")
    sqlFileD.write(queryDistrict)

def createQuerys(table, dictionaryData):
    keysTuple = ', '.join(dictionaryData.keys())
    valuesTuple = ', '.join(dictionaryData.values())
    return "Insert Into %s (%s) Values (%s) ;" % (table, keysTuple, valuesTuple)


def loadDataCodelec(path):
    txtFile = ""
    try:
        txtFile = open(path)
    except:
        print("Can't read this path..")
        return
    linesList = txtFile.readlines()
    for line in linesList:
        splitLineCodelec(line)


def defineParameters():
    path = '/home/miguelmendezrojas/Descargas/padron_completo/PADRON_COMPLETO.txt'
    pathDistelec = '/home/miguelmendezrojas/Descargas/padron_completo/Distelec.txt'
    round = 15

    loadDataCodelec(pathDistelec)
    loadData(path, round)

defineParameters()
