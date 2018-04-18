import json
'''
处理历史最高记录
'''

def getRecord():
	with open('record.json', 'r') as f:
		data = json.load(f)
	return data['score']

def setRecord(score):
	data={'score':score }
	with open('record.json', 'w') as f:
		json.dump(data,f)
