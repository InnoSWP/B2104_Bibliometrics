from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
import time
from datetime import datetime

# Create your views here.

def get(request, name, token):
	try:
		db = open('/Users/grisharybolovlev/IU/bibliometrics/bibliometrics/api/assets/' + str(name) + '.csv', 'rb')

		return FileResponse(db)

	except:
		return HttpResponse('No such file or your request is processing!')



def update(request, token):
	now = datetime.now()
	current_time = now.strftime("%Y/%m/%d-%H:%M:%S")
	return HttpResponse('DB will be uploaded with name "' + current_time + '"')