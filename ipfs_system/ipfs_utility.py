import os
import uuid
import inspect
import requests
import netifaces as ni
import psutil

from app_config import *

class IPFSUtility(object):

	def __init__(self):
		pass

	def __del__(self):
		pass

	def get_dir_size(self, fqdp):

		total_size = 0

		try:
			for path, dirs, files in os.walk(fqdp):
				for f in files:
					fp = os.path.join(path, f)
					total_size += os.path.getsize(fp)
		except Exception as err:
			print(err)

		return total_size

	def get_file_size(self, fqfp):

		return os.path.getsize(fqfp)
		
	def get_host_ip(self):
		
		ip = None
		
		try:
			ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
		except Exception as err:
			print(err)
		
		return ip		
	
	def download_file(self,file_path,url):

		status = True
		
		try:
			with requests.get(url, stream=True) as r:
				with open(file_path, 'wb') as f:
					for chunk in r.iter_content(chunk_size=8192): 
						if chunk: # filter out keep-alive new chunks
							f.write(chunk)
							f.flush()
		except:
			status = False
			
		return status
		
	def create_unique_filename(self, hash):
		
		filename = inspect.getframeinfo(inspect.currentframe()).filename
		path = os.path.dirname(os.path.abspath(filename))
		
		temp_filename = "ipfs_%s_%s" % (hash,uuid.uuid4().hex)
		
		temp_fp = os.path.join(path, FILE_STASH_DIR, temp_filename)
		
		return temp_fp
		
	def get_app_path(self):
		
		path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
		
		return path
		
	def get_pid_listening_to_port(self, target_port):
		
		pid = None
		
		lc = psutil.net_connections('inet')
		
		for c in lc:
			(ip, port) = c.laddr
			if port == target_port:
				pid = c.pid
				break
				
		return pid
		
		
