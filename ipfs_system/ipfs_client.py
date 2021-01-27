import requests
import simplejson as json
import logging

from ipfs_utility import *

log = logging.getLogger(__name__)

class IPFSClient(object):

	def __init__(self):
		self.utility = IPFSUtility()

	def __del__(self):
		pass

	def upload_file(self, file_path, server_details):
		status = True
		hash = None

		try:
			api_port = server_details["api_port"]

			files = {'file': open(file_path, 'rb')}

			r = requests.post("http://127.0.0.1:%s/api/v0/add" % api_port, files=files)

			if r.status_code == 200:
				hash = json.loads(r.text)["Hash"]
			else:
				raise Exception("IPFS FILE UPLOAD FAILED")

		except Exception as err:
			log.error(err)
			status = False

		return (status, hash)

	def pin_hash(self,hash,server_details):

		status = True

		try:
			api_port = server_details["api_port"]

			params = {}
			params["arg"] = hash

			r = requests.get("http://127.0.0.1:%s/api/v0/pin/add" % api_port, params=params)

			if r.status_code != 200:
				raise Exception("IPFS PIN FAILED")

		except Exception as err:
			log.error(err)
			status = False

		return status

	def delete_file(self, file_hash, server_details):
		status = True

		try:
			api_port = server_details["api_port"]

			params = {}
			params["arg"] = file_hash

			r = requests.get("http://127.0.0.1:%s/api/v0/pin/rm" % api_port, params=params)
			if r.status_code != 200:
				raise Exception("IPFS FILE DELETE FAILED")
			else:
				status = self.garbage_collect(server_details)
				
		except Exception as err:
			log.error(err)
			status = False

		return status

	def shutdown(self, server_details):
		status = True

		try:
			api_port = server_details["api_port"]
			r = requests.get("http://127.0.0.1:%s/api/v0/shutdown" % api_port)
			if r.status_code != 200:
				raise Exception("IPFS SHUTDOWN FAILED")
				
		except Exception as err:
			log.error(err)
			status = False

		return status

	def ping(self, server_details):
		status = True

		try:
			api_port = server_details["api_port"]
			r = requests.get("http://127.0.0.1:%s/api/v0/id" % api_port)
			
			if r.status_code != 200:
				raise Exception("IPFS PING FAILED")
				
		except Exception as err:
			log.error(err)
			status = False

		return status

	def garbage_collect(self, server_details):
		status = True

		try:
			api_port = server_details["api_port"]
			r = requests.get("http://127.0.0.1:%s/api/v0/repo/gc" % api_port)
			if r.status_code != 200:
				raise Exception("IPFS GARBAGE COLLECTION FAILED")
				
		except Exception as err:
			log.error(err)
			status = False

		return status
		
	def download_ipns_file(self, hash, temp_fp):
		status = True

		try:
			ipns_url = "http://ipfs.io/ipns/%s" %  hash
			status = self.utility.download_file(temp_fp, ipns_url)
		except Exception as err:
			log.error(err)
			status = False

		return status

	def create_ipns_key(self, key, server_details):
		
		status = True
		ipns_hash = None

		try:
			api_port = server_details["api_port"]
			
			params = {}
			params["arg"] = key
			params["type"] = "rsa"
			params["size"] = 2048
			
			r = requests.get("http://127.0.0.1:%s/api/v0/key/gen" % api_port, params = params)
			
			if r.status_code == 200:
				ipns_hash = json.loads(r.text)["Id"]
			else:
				raise Exception("GENERATE IPNS KEY:%s FAILED" % key)
				
		except Exception as err:
			log.error(err)
			status = False

		return status, ipns_hash
		
	def publish_key(self, key, ipfs_hash, lifetime, server_details):
		
		status = True

		try:
			api_port = server_details["api_port"]
			
			params = {}
			params["arg"] = ipfs_hash
			params["key"] = key
			params["lifetime"] = lifetime
			
			r = requests.get("http://127.0.0.1:%s/api/v0/name/publish" % api_port, params = params)
			
			if r.status_code != 200:
				log.info(r.text)
				raise Exception("PUBLISH IPNS FAILED")
				
		except Exception as err:
			log.error(err)
			status = False

		return status
		
	def remove_ipns_key(self, key, server_details):
		
		status = True
		ipns_hash = None

		try:
			api_port = server_details["api_port"]
			
			params = {}
			params["arg"] = key
			
			r = requests.get("http://127.0.0.1:%s/api/v0/key/rm" % api_port, params = params)
			
			if r.status_code != 200:
				raise Exception("REMOVE IPNS KEY:%s FAILED" % key)
				
		except Exception as err:
			log.error(err)
			status = False

		return status, ipns_hash
	
	def get_ipns_keys(self, server_details):
		
		status = True
		key_map = {}

		try:
			api_port = server_details["api_port"]
			
			r = requests.get("http://127.0.0.1:%s/api/v0/key/list" % api_port)
			
			if r.status_code == 200:
				
				data = json.loads(r.text)
				
				for info in data["Keys"]:
					key_map[info["Name"]] = info["Id"]
			else:
				raise Exception("GET IPNS KEYS FAILED")
				
		except Exception as err:
			log.error(err)
			status = False

		return status, key_map


