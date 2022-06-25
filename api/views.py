from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
from .settings import TOKEN
import time
from datetime import datetime
import asyncio
import os
import pathlib
# Create your views here.

def get(request, name, token):
	if token == TOKEN:
		try:
			db = open(str(pathlib.Path(__file__).parent.resolve()) + '/assets/' + str(name) + '.csv', 'rb')

			return FileResponse(db)

		except:
			return HttpResponse('No such file or your request is processing!')
	else:
		return HttpResponse('Invalid token')

def update(request, token):
	if token == TOKEN:
		now = datetime.now()
		current_time = now.strftime("%Y/%m/%d-%H:%M:%S")
		return HttpResponse('DB will be uploaded with name "' + current_time + '"')
	else:
		return HttpResponse('Invalid token')