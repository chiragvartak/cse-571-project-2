import sys, types, time, random, os

def transpose(layoutName):
    file = "layouts/%s.lay" % layoutName
    transposeFile = "layouts/%sT.lay" % layoutName
    with open(file, 'r') as f:
        array = f.read()

    rows = array.split("\n")
    with open(transposeFile, 'w') as f:
        for j in range(len(rows[0])):
            for row in rows:
                if row != '':
                    f.write(row[j])
            if j != len(rows[0])-1:
                f.write("\n")

    return "%sT" % layoutName

def flip(layoutName):
    file = "layouts/%s.lay" % layoutName
    flipFile = "layouts/%sF.lay" % layoutName
    with open(file, 'r') as f:
        array = f.read()

    rows = array.split("\n")
    with open(flipFile, 'w') as f:
        for i in range(len(rows)):
            row = rows[i]
            for j in range(len(rows[0])-1,-1,-1):
                if row != '':
                    f.write(row[j])
            if i != len(rows)-1:
                f.write("\n")

    return "%sF" % layoutName

def generate(layoutName):
    layoutT = transpose(layoutName)
    layoutF = flip(layoutName)
    layoutTF = flip(layoutT)
    layoutFT = transpose(layoutF)
    layoutFTF = flip(layoutFT)
    layoutTFT = transpose(layoutTF)
    layoutTFTF = flip(layoutTFT)

def stringOfNames(layoutNames):
    stringOfNames = ""
    for n in layoutNames:
        generate(n)
        stringOfNames += "%s-%sF-%sFT-%sFTF-%sT-%sTF-%sTFT-%sTFTF-" % (n, n, n, n, n, n, n, n)
        n += "Capsule"
        generate(n)
        stringOfNames += "%s-%sF-%sFT-%sFTF-%sT-%sTF-%sTFT-%sTFTF-" % (n, n, n, n, n, n, n, n)

    return stringOfNames[0:-1]

if __name__ == '__main__':
    args = sys.argv[1:]
    print(stringOfNames(args))