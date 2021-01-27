import signal
import sys
import os
import time
import logging


from paste import httpserver
from multiprocessing import Process, Value

from ipfs_api import app
from ipfs_manager import *
from ipfs_utility import *
from app_config import *



app_path = IPFSUtility().get_app_path()
logging.basicConfig(filename=os.path.join(app_path,LOG_DIR,'app.log'),level=logging.INFO,format='%(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class PIDSingleton(object):
	
	__instance = None
	
	def __init__(self):
		
		self.API_PID = None
		self.BACKGROUND_WORKER_PID = None
		
	def get_instance(self):
		
		if not PIDSingleton.__instance:
			PIDSingleton.__instance = self
			
		return PIDSingleton.__instance
		

class IPFSAPI(Process):

	def __init__(self):

		super(IPFSAPI, self).__init__()
		
	def __del__(self):
		log.info("EXITING IPFS API")
		raise httpserver.ServerExit(3)

	def run(self):
		httpserver.serve(app, host='0.0.0.0', port=API_PORT)

class BackgroundWorker(Process):

	def __init__(self):

		super(BackgroundWorker, self).__init__()
		
	def __del__(self):
		log.info("EXITING BACKGROUND WORKER")

	def run(self):

		manager = IPFSManager()

		while True:

			manager.upload_file_to_server()
			manager.delete_file_from_server()
			manager.delete_key_from_server()

			time.sleep(2)
			

class AppRunner():
	
	def __init__(self):
		
		log.info("IPFS APP RUNNER CREATED")
		self.API_PID = Value('i', 0)
		self.BACKGROUND_WORKER_PID = Value('i', 0)
	
	def __del__(self):
		print("Deleting ...")
		self.graceful_exit()
		
	def graceful_exit(self, signum=None, frame=None):

		print("GRACEFUL EXIT HANDLER INVOKED !")
		
		s = PIDSingleton().get_instance()

		if self.API_PID.value != 0:
			log.info("TERMINATING API PID: %s" % self.API_PID.value)
			os.kill(self.API_PID.value, signal.SIGINT)
			self.API_PID.value = 0

		if self.BACKGROUND_WORKER_PID.value != 0:
			log.info("TERMINATING WORKER PID: %s" % self.BACKGROUND_WORKER_PID.value)
			os.kill(self.BACKGROUND_WORKER_PID.value, signal.SIGINT)	
			self.BACKGROUND_WORKER_PID.value = 0
	
	def start(self):
		
		log.info("================ START IPFS SYSTEM ================")
		
		signal.signal(signal.SIGTERM, self.graceful_exit)
		signal.signal(signal.SIGINT, self.graceful_exit)
		#signal.signal(signal.SIGUSR1, self.graceful_exit)
		
		# START SERVERS
		
		manager = IPFSManager()
		manager.start_servers()

		# == LAUNCH API ==
		app_api = IPFSAPI()
		app_api.start()
		api_pid = app_api.pid
		log.info("API PID: %s" % api_pid)

		# == LAUNCH FILE WORKER ==
		background_worker = BackgroundWorker()
		background_worker.start()
		background_worker_pid = background_worker.pid
		log.info("BACKGROUND WORKER PID: %s" % background_worker_pid)
		
		self.API_PID.value = api_pid
		self.BACKGROUND_WORKER_PID.value = background_worker_pid

		# wait for the api and worker to exit
		app_api.join()
		background_worker.join()


def main():
	r = AppRunner()
	r.start()


if __name__ == "__main__":
	
	r = AppRunner()
	r.start()