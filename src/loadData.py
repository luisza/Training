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

    print(len(linesList))

    for line in linesList:
        dictionaryToSave = splitLine(line)
        dictionaryList.append(dictionaryToSave)
        if(count>max_len):
            tuple = dictionaryListToValues(dictionaryList)
            saveLine(tuple)
            dictionaryList = []
            count = 0
        count+=1

    print("Success")

def dictionaryListToValues(dictionaryList):
    tupleList = [tuple(element.values()) for element in dictionaryList]
    tupleString = ""
    for element in tupleList:
        #this validation is because mysql does not recognize a comma at the end of the values
        if(tupleList[-1]==element):
            tupleString += "%s " % str(element)
        else:
            tupleString += "%s, " % str(element)
    return tupleString


def saveLine(values):
   # columns = ', '.join(dictionaryToSave.keys())
    sql = "INSERT INTO %s (lastname1, board, cad_date, lastname2, gender, fullName, idCard, codelec, name) VALUES %s;"% ('Elector', values)
    sqlFile = open("querys.sql", "a")
    sqlFile.write(sql)

  #  cursor.execute(sql, dictionaryToSave.values())

def splitLine(line):
    split = line.split(",")
    fullName= "%s %s %s" % (split[5].strip(),split[6].strip(),split[7].strip())
    orderedInfo = {
                    'idCard':   split[0],
                    'codelec':  split[1],
                    'gender' :  split[2],
                    'cad_date': split[3],
                    'board' :   split[4],
                    'fullName': fullName,
                    'name' :    split[5].strip(),
                    'lastname1': split[6].strip(),
                    'lastname2': split[7].strip()
                }
    return orderedInfo

def defineParameters():
    path = '/home/miguelmendezrojas/Descargas/padron_completo/PADRON_COMPLETO.txt'
    round = 15
    loadData(path, round)

defineParameters()