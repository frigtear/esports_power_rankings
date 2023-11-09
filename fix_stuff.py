import json
#This is a digusting python file I wrote to reformat my json file because I messed up whoops
e = []
with open('clean_data.json') as f:
    data = f.readlines()
    for dat in data:
        #print(dat.strip())
        e.append(dat.strip())
    ej = ''.join(e)
    sp = ej.split(',')
    sp = sp[1:]
    #print(sp[0])
    col = []
    for item in sp[1:]:
        #rint(item)
        id = item.split(':')[0]
        #rint((id, item))
        if len(id) > 14 and not 'first' in id and not 'turr' in id and not "games" in id:
            #print(id)
            col.append(id)
            col.append(item.split(':')[1].replace('{','').strip() +':' + item.split(':')[2].strip())
        elif len(item) < 30 :
            col.append(item)


    #print(col)
dictList = []
subCol = []
newCol = []


col = col[7:]
#print(col)
for c in col:
    if len(c) > 14 and not 'first' in c and not 'turr' in c and not "games" in c:
        newCol.append(subCol)
        subCol = []
    subCol.append(c)

newCol = newCol[1:]
dictList = []
subDict = {}
for n in newCol:
    pid = n[0].replace("\"",'')
    pid = pid.replace('{','')
    subDict[pid] = {}
    for _ in n[1:]:
        s = _.split(':')
        key = s[0].replace("\"",'')
        try:
            value = s[1]
        except IndexError:
            value = '0'
        subDict[pid][key] = int(value.replace('}','').strip())
    #print(subDict)
    dictList.append(subDict)
    #print(len(dictList))
    subDict = {}
#print(dictList)
with open('fixed_json.json','w') as f:
    json.dump(dictList,f)

