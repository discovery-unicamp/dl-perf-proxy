import json
string = ''
while True:
    try:
        string += input() + '\n'
    except EOFError:
        break
dic = json.loads(string)
for event in dic['events']:
    print(event['message'])
