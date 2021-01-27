from ipfs_registrar import *
from ipfs_client import *
from ipfs_server import *
from ipfs_utility import *
from app_config import *

import random
import os
import signal
from multiprocessing import Process, Manager
import simplejson as json
import logging

log = logging.getLogger(__name__)

class IPFSManager(object):

	def __init__(self):
		self.registrar = IPFSRegistrar()
		self.client = IPFSClient()
		self.utility = IPFSUtility()
		

	def __del__(self):
		pass


	def register_server(self, params):
		
		server = None
		status, id = self.registrar.register_server(params)

		if id:
			temp_server = IPFSServer(params)
			status, peer_id = temp_server.initialize_repository()

			if peer_id:
				status = self.registrar.update_server(id, {"peer_id" : peer_id})
				status = temp_server.reconfigure()
						
			status, server = self.registrar.get_server(id)

		return (status,server)
		

	def update_server(self, id, params):

		status, server = self.registrar.get_server(id)
		pid = None

		if server:
			
			ping_status = self.client.ping(server)
			if ping_status:
				pid = self.utility.get_pid_listening_to_port(server["api_port"])
				if pid:
					os.kill(pid, signal.SIGINT)

			status = self.registrar.update_server(id, params)
			status, server = self.registrar.get_server(id)

			temp_server = IPFSServer(server)
			status = temp_server.reconfigure()

			if ping_status:
				status, pid  = temp_server.start()

		return (status, server, pid)
		

	def delete_server(self, id):

		status, server = self.registrar.get_server(id)

		if server:
			status = self.client.ping(server)
			if status:
				pid = self.utility.get_pid_listening_to_port(server["api_port"])
				if pid:
					os.kill(pid, signal.SIGINT)
					
			status = self.registrar.unset_files_by_server(id)
			status = self.registrar.delete_server(id)

		return status
		

	def get_servers(self, page, chunk):
		start_index = (page-1) * chunk
		status, servers = self.registrar.get_servers(start_index, chunk)

		return (status, servers)
		

	def start_server(self, id):

		ret_status = False
		
		status, server = self.registrar.get_server(id)
		pid = None

		if server:
			status = self.client.ping(server)
			
			if status:
				log.info("SERVER IS STILL ALIVE")
				ret_status  = False # if server is still alive
			else:
				temp_server = IPFSServer(server)
				ret_status, pid  = temp_server.start()				

		return (ret_status, pid)
		
		
	def start_servers(self):

		status, servers = self.registrar.get_all_servers()
		
		for server in servers:
			api_port = server["api_port"]
			swarm_port = server["swarm_port"]
			gateway_port = server["gateway_port"]			
			
			log.info("STARTING SERVER => API PORT : %s   SWARM PORT : %s   GATEWAY PORT : %s" % (api_port, swarm_port, gateway_port)) 
				
			status = self.client.ping(server)
				
			if status:
				log.info("SERVER IS STILL ACTIVE")
			else:
				temp_server = IPFSServer(server)
				status, pid  = temp_server.start()
				
				if pid:
					log.info("SERVER START SUCCESS")
				else:
					log.info("SERVER START FAIL")
					

	def restart_server(self, id):
		status, server = self.registrar.get_server(id)
		pid = None

		if server:
			status = self.client.ping(server)
			if status:
				temp_pid = self.utility.get_pid_listening_to_port(server["api_port"])
				if temp_pid:
					os.kill(temp_pid, signal.SIGINT)

			temp_server = IPFSServer(server)
			status, pid  = temp_server.start()

		return (status, pid)


	def stop_server(self, id):
		ret_status = False
		
		status, server = self.registrar.get_server(id)

		if server:
			status = self.client.ping(server)
			if status:
				pid = self.utility.get_pid_listening_to_port(server["api_port"])
				if pid:
					os.kill(pid, signal.SIGINT)
					ret_status = True
		else:
			status = False

		return ret_status
		

	def ping_server(self, id):
		status, server = self.registrar.get_server(id)

		if server:
			status = self.client.ping(server)
		else:
			status = False

		return status
		

	def upload_file(self, params):
		
		file = None

		fqfp = params["fqfp"]
		filename = fqfp[fqfp.rfind(os.path.sep)+1:]
		params["filename"] = filename
		params["size"] = self.utility.get_file_size(fqfp)

		status, id = self.registrar.register_file(params)
		
		if id:
			status, file = self.registrar.get_file(id)

		return (status, file)
		

	def update_file(self, id, params):
		status = self.registrar.update_file(id, params)

		return status
		

	def delete_file(self, id):

		status, file = self.registrar.get_file(id)

		if file:
			status = self.registrar.mark_file_for_deletion(id)
		else:
			status = False

		return status
		

	def get_files(self, page, chunk):
		start_index = (page-1) * chunk
		status, files = self.registrar.get_files(start_index, chunk)

		return (status, files)
		

	def upload_file_to_server(self):

		ret_status = False
		
		hash = None
		status, file = self.registrar.get_file_for_upload()

		if file:

			fid = file["id"]
			fqfp = file["fqfp"]
			server_id = file["server_id"]
			
			self.registrar.update_file(fid,{"upload_status" : PENDING})
			
			status, server = self.registrar.get_server(server_id)
			
			if server:
				status, hash = self.client.upload_file(fqfp, server)

				if hash:
					log.info("UPLOADED FILE: %s" % fqfp)
					ret_status = self.client.pin_hash(hash, server)
					self.registrar.update_file(fid,{"ipfs_hash" : hash})
					
					
			if ret_status:
				self.registrar.update_file(fid,{"upload_status" : SUCCESS})
			else:
				self.registrar.update_file(fid,{"upload_status" : FAIL})	
				
			
		return (ret_status, hash)
		

	def delete_file_from_server(self):

		ret_status = False
		
		status, file_rec = self.registrar.get_file_for_deletion()

		if file_rec:
			
			log.info("DELETING KEY REC : %s" % file_rec["id"])

			server_id = file_rec["server_id"]
			hash = file_rec["ipfs_hash"]
			file_id = file_rec["id"]
			
			status, server = self.registrar.get_server(server_id)

			if server:
				
				status = self.client.ping(server)
				
				if status:

					status = self.client.delete_file(hash, server)

					if status:
						ret_status = self.registrar.delete_file(file_id)

		return ret_status
		
		
	def download_ipns_file(self,hash):
		
		ret_status = False
		stash_file = None
		
		stash_file = self.utility.create_unique_filename(hash)
		ret_status = self.client.download_ipns_file(hash, stash_file)

		return (ret_status, stash_file)
		
		
	def create_ipns_key(self, params):
		
		ipns_hash = None
		key_rec = None
		
		key = params["key"]
		server_id = params["server_id"]
		
		status, key_rec = self.registrar.get_ipns_key_by_name(key)
		
		if not key_rec:
		
			status, server = self.registrar.get_server(server_id)
			
			if server:
				status = self.client.ping(server)
				if status:
					
					status, key_map = self.client.get_ipns_keys(server)
						
					if key in key_map:
						
						ipns_hash = key_map[key]
					else:
						status, ipns_hash = self.client.create_ipns_key(key,server)
					
					if ipns_hash:
						entry = {}
						entry["key"] = key
						entry["ipns_hash"] = ipns_hash
						entry["server_id"] = server_id
						
						status, key_id = self.registrar.register_ipns_key(entry)
						status, key_rec = self.registrar.get_ipns_key(key_id)					
		
		return (status, key_rec)
		
	
	def get_ipns_keys(self, page, chunk):
		start_index = (page-1) * chunk
		status, servers = self.registrar.get_ipns_keys(start_index, chunk)

		return (status, servers)
		
		
	def publish_key(self, params):
	
		ret_status = False
		file_data = None
		
		key_id = params["key_id"]
		file_id = params["file_id"]
		ttl = params["ttl"]
		
		status, file_rec = self.registrar.get_file(file_id)
		status, key_rec = self.registrar.get_ipns_key(key_id)
		
		if file_rec and key_rec:
			
			if file_rec["ipfs_hash"] != "":
				
				if file_rec["server_id"] == key_rec["server_id"] and file_rec["server_id"] != 0:
					
					server_id = file_rec["server_id"]
					ipfs_hash = file_rec["ipfs_hash"]
					key = key_rec["key"]					

					status, server = self.registrar.get_server(server_id)
					
					if server:
						status = self.client.ping(server)
						if status:
							ret_status = self.client.publish_key(key, ipfs_hash, ttl, server)	
							if ret_status:
								status = self.registrar.update_file(file_id,{"ipns_key_id": key_id})
								status, file_rec = self.registrar.get_file(file_id)
								file_data = file_rec.serialize()
								key_data = key_rec.serialize()
								file_data["ipns_info"] = key_data
								ret_status = True
		else:
			log.info("EITHER FILE OR KEY OR BOTH RECORDS DOES NOT EXIST")
			
		return (ret_status, file_data)
		
	
	def delete_ipns_key(self, id):

		status, key_rec = self.registrar.get_ipns_key(id)

		if key_rec:
			status = self.registrar.mark_key_for_deletion(id)
		else:
			status = False

		return status
		
	
	def delete_key_from_server(self):

		ret_status = False
		status, key_rec = self.registrar.get_key_for_deletion()

		if key_rec:
			
			log.info("DELETING KEY RECORD : %s" % key_rec["id"])

			server_id = key_rec["server_id"]
			key_id = key_rec["id"]
			key = key_rec["key"]
			
			status, server = self.registrar.get_server(server_id)

			if server:
				
				status = self.client.ping(server)
				
				if status:

					status = self.client.remove_ipns_key(key, server)
					
					if status:
						ret_status = self.registrar.delete_key(key_id)

		return ret_status
		
	def stop_all_servers(self):
		
		status, servers = self.registrar.get_all_servers()
		
		for server in servers:
			api_port = server["api_port"]
			swarm_port = server["swarm_port"]
			gateway_port = server["gateway_port"]			
			
			log.info("STOPPING SERVER => API PORT : %s   SWARM PORT : %s   GATEWAY PORT : %s" % (api_port, swarm_port, gateway_port)) 
			
			pid = self.utility.get_pid_listening_to_port(api_port)
			if pid:
				log.info("PID %s LISTENING AT PORT %s" % (pid, api_port))
				os.kill(pid, signal.SIGINT)
				
	def  is_enough_storage(self,params):

		status = False
		
		fqfp = params["fqfp"]
		server_id = params["server_id"]
		
		fsize = self.utility.get_file_size(fqfp)
		
		log.info("FILE SIZE: %s" % fsize)
				
		status, server = self.registrar.get_server(server_id)
		
		if server:
			max_dir_size = server["max_dir_size"] * 1024 * 1024 * 1024
			status, total_size = self.registrar.get_sum_file_size_by_server(server_id)
			
			log.info("MAX DIR SIZE: %s" % max_dir_size)
			log.info("ACTUAL DIR SIZE: %s" % max_dir_size)
			
			if (total_size + fsize) < max_dir_size:
				status = True	
		
		return status