import json

with open('input.json,'r') as f:
    inputjson = json.load(f)

Remove element from json object 
Json to python conversion
Object -> Dict
Array -> List
String ->str
false ->False
null -> None

#Remove element crime from state Object
for state in inputjson['states']:
    del state['crime']
#export python dict to Json file

with open('output.json','w') as w:
    json.dump(inputjson,w,indent=2)


####
get and parse json from feed or site

import jsonfrom urllib.request import urlopen

with urlopen('https://mysite') as response:
    source = response.read()
#convert string to python object
data = json.loads(source)

