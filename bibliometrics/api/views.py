from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse, HttpResponse
from .settings import TOKEN
from datetime import datetime
import time
import pathlib
import threading
from scraping.parse import Scraper
import subprocess, shlex

@api_view(['POST'])
def getData(request):

	if request.data['api-key'] and request.data['api-key'] == TOKEN:
		try:
			return Response(open(f'{str(pathlib.Path(__file__).parent.resolve())}/assets/{request.data["file-name"]}', 'rb'))
		except:

			return Response({'code' : 'Wrong file name or file is processing'})
	else:
		return Response({'code' : 'Wrong api token'})


@api_view(['POST'])
def processData(request):
	if request.data['api-key'] and request.data['api-key'] == TOKEN:

		now = datetime.now()
		current_time = now.strftime("%Y/%m/%d-%H:%M:%S")
		#scraper = Scraper()
		#scraper.parse()
		cmd = f"python3 {print(str(pathlib.Path(__file__).parent.resolve())[:-17])}main.py"
		args = shlex.split(cmd)
		subprocess.Popen(args, shell=True)


		return Response({'name' : f'{str(current_time)}',
			'state' : 'processing'})
		
	else:
		return Response({'code' : 'Wrong api token'})



