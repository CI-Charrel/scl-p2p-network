import os
import subprocess
import simplejson as json
import platform
import shlex
import inspect
import logging

from subprocess import Popen, PIPE
from ipfs_utility import *
from app_config import *

log = logging.getLogger(__name__)

class IPFSServer(object):

	def __init__(self, details):
		self.details = details
		self.utility = IPFSUtility()

	def __del__(self):
		pass

	def get_windows_ipfs_exe_dir(self):

		filename = inspect.getframeinfo(inspect.currentframe()).filename
		path = os.path.dirname(os.path.abspath(filename))

		exe_dir = os.path.join(path, IPFS_WIN_EXE_DIR)

		return exe_dir

	def initialize_repository(self):

		status = True
		peer_id = None

		try:
			target_dir = self.details["directory"]

			env_vars = os.environ.copy()
			env_vars["IPFS_PATH"] = target_dir

			config_file = os.path.join(target_dir,IPFS_CONFIG_FILE)

			if not os.path.exists(config_file):

				log.info("INITIALIZING IPFS REPO: %s" % target_dir)

				cmd = None

				operating_system = platform.system()

				if operating_system == "Windows":
					log.info("WINDOWS DETECTED")
					win_exe_dir = self.get_windows_ipfs_exe_dir()
					cmd = "%s init" % os.path.join(win_exe_dir, IPFS_WIN_EXE)
				elif operating_system == "Linux":
					log.info("LINUX DETECTED")
					cmd = "ipfs init"
				else:
					status = False

				if cmd:
					cmd_tokens = cmd.split(" ")
					shell = Popen(cmd_tokens, cwd=target_dir, env=env_vars, stdin=PIPE, stdout=PIPE, stderr=PIPE)
					shell.communicate()

			config_data = {}

			with open(config_file) as f:
				config_data = json.loads(f.read())

			peer_id = config_data["Identity"]["PeerID"]

		except Exception as err:
			print(err)
			status = False

		return status, peer_id

	def reconfigure(self):
		status = True

		try:
			host_ip = self.utility.get_host_ip()
			target_dir = self.details["directory"]
			target_swarm_port = self.details["swarm_port"]
			target_api_port = self.details["api_port"]
			target_gateway_port = self.details["gateway_port"]

			config_file = os.path.join(target_dir,IPFS_CONFIG_FILE)

			config_data = {}

			with open(config_file) as f:
				config_data = json.loads(f.read())

			peer_id = config_data["Identity"]["PeerID"]

			swarm_addresses = config_data["Addresses"]["Swarm"]
			api_address = config_data["Addresses"]["API"]
			gateway_address = config_data["Addresses"]["Gateway"]

			# modify swarm_addresses
			swarm_port = swarm_addresses[0].split("/")[-1]
			modified_swarm_addresses = []
			for sa in swarm_addresses:
				temp_sa = sa.replace(swarm_port,str(target_swarm_port))
				modified_swarm_addresses.append(temp_sa)

			config_data["Addresses"]["Swarm"] = modified_swarm_addresses

			# modify api_address
			api_port = api_address.split("/")[-1]
			api_address = api_address.replace(api_port,str(target_api_port))

			config_data["Addresses"]["API"] = api_address

			# modify api_address
			gateway_port = gateway_address.split("/")[-1]
			gateway_address = gateway_address.replace(gateway_port,str(target_gateway_port))

			config_data["Addresses"]["Gateway"] = gateway_address

			# modify api to support CORS
			config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Credentials"] = ["true"]
			config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Methods"] = ["PUT", "GET", "POST"]
			config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Origin"] = []
			config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Origin"].append("http://%s:%s" % (host_ip,target_api_port))
			config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Origin"].append("https://webui.ipfs.io")

			# modify bootstrap list
			#if is_private:
			#	config_data["Bootstrap"] = []
			#	config_data["Bootstrap"].append("/ip4/%s/tcp/%s/ipfs/%s" % (host_ip, target_swarm_port, peer_id))

			with open(config_file,"w") as f:
				config_str = json.dumps(config_data)
				f.write(config_str)

		except Exception as err:
			print(err)
			status = False

		return status

	def start(self):	
		
		status = True
		pid = 0

		try:
			target_dir = self.details["directory"]
			
			log.info("STARTING DAEMON: %s" % target_dir)

			env_vars = os.environ.copy()
			env_vars["IPFS_PATH"] = target_dir

			operating_system = platform.system()

			cmd = None

			if operating_system == "Windows":
				log.info("WINDOWS DETECTED")
				flags = 0
				flags |= 0x00000008  # DETACHED_PROCESS
				flags |= 0x00000200  # CREATE_NEW_PROCESS_GROUP
				flags |= 0x08000000  # CREATE_NO_WINDOW
				#si = subprocess.STARTUPINFO()
				#si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				win_exe_dir = self.get_windows_ipfs_exe_dir()
				cmd = "%s daemon" % os.path.join(win_exe_dir, IPFS_WIN_EXE)
				cmd_tokens = cmd.split(" ")
				pid = Popen(cmd_tokens, cwd=target_dir, env=env_vars, creationflags=flags, stdin=PIPE, stdout=PIPE, stderr=PIPE).pid
			elif operating_system == "Linux":
				log.info("LINUX DETECTED")
				cmd = "ipfs daemon"
				cmd_tokens = cmd.split(" ")
				pid = Popen(cmd_tokens, cwd=target_dir, env=env_vars, stdin=PIPE, stdout=PIPE, stderr=PIPE).pid #note: redirect to devnull stdout
			else:
				status = False
		except Exception as err:
			print(err)
			status = False

		return status, pid

