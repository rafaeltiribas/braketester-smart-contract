import json

class ConverterData(object):

    def __init__(self):
        self._data = None


    print("ConverterData")


    def conversor(self, filename=None):

        timestamp = []
        equip1 =[]
        equip2 = []
        equip3 = []
        equip4 = []

        print(filename)
        # path to the folder holding the txt
        # directory = '/path/to/folder'
        directory = filename

        # iterate over the txt files in the folder
        if filename.endswith(".txt"):
            print("identifiquei o arquivo")
            with open(filename, "r", encoding ="utf-8") as ficheiro:
                f = ficheiro.readlines()
                splitcontent = f[22:-1]

                for v in splitcontent:
                    v = v.split(sep=',', maxsplit=9)
                    timestamp.append(v[0])
                    equip1.append((v[1]))
                    equip2.append((v[2]))
                    equip3.append((v[3]))
                    equip4.append((v[4]))

            jsonStructure = {
                "Timestamp": timestamp,
                "Medidor1": equip1,
                "Medidor2": equip2,
                "Medidor3": equip3,
                "Medidor4": equip4,
            }
            j = json.dumps(jsonStructure, indent=4)


            filename = filename.replace('.txt', '')
            output_file = open(filename + '.json', 'w')
            output_file.write(j)
            #parsed = json.loads(j)

            self._data = j

            return self._data
        else:
            return None
