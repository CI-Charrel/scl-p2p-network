from orator import DatabaseManager
from db_config import DATABASES
from app_config import *
import logging

log = logging.getLogger(__name__)

class IPFSRegistrar(object):

	def __init__(self):
		self.db = DatabaseManager(DATABASES)

	def __del__(self):
		pass

	def register_server(self, params):
		
		status = True
		id = None

		try:
			id = self.db.table('ipfs_servers').insert_get_id(params)
		except Exception as err:
			log.error(err)
			status = False

		return (status, id)

	def update_server(self, id, params):
		status = True

		try:
			self.db.table('ipfs_servers').where('id', id).update(params)
		except Exception as err:
			log.error(err)
			status = False

		return status

	def delete_server(self, id):
		status = True

		try:
			self.db.table('ipfs_servers').where('id', id).delete()
		except Exception as err:
			log.error(err)
			status = False

		return status

	def get_server(self, id):
		status = True
		server = None

		try:
			server = self.db.table('ipfs_servers').where('id', id).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, server)

	def get_servers(self, start_index, chunk):

		status = True
		servers = []

		try:
			servers = self.db.table('ipfs_servers').offset(start_index).limit(chunk).get()
		except Exception as err:
			log.error(err)
			status = False

		return (status, servers)

	def get_all_servers(self):

		status = True
		servers = []

		try:
			servers = self.db.table('ipfs_servers').get()
		except Exception as err:
			log.error(err)
			status = False

		return (status, servers)

	def register_file(self, params):
		
		status = True
		id = None

		try:
			id = self.db.table('ipfs_files').insert_get_id(params)
		except Exception as err:
			log.error(err)
			status = False

		return (status, id)

	def update_file(self, id, params):
		
		status = True

		try:
			self.db.table('ipfs_files').where('id', id).update(params)
		except Exception as err:
			log.error(err)
			status = False

		return status

	def delete_file(self, id):
		status = True

		try:
			self.db.table('ipfs_files').where('id', id).delete()
		except Exception as err:
			log.error(err)
			status = False

		return status

	def get_file(self, id):
		
		status = True
		file = None

		try:
			file = self.db.table('ipfs_files').where('id', id).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, file)
		
	def get_file_by_hash(self, hash):
		
		status = True
		file = None

		try:
			file = self.db.table('ipfs_files').where('ipfs_hash', hash).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, file)

	def get_files(self, start_index, chunk):

		status = True
		files = []

		try:
			files = self.db.table('ipfs_files').offset(start_index).limit(chunk).get()
		except Exception as err:
			log.error(err)
			status = False

		return (status, files)

	def get_files_by_server_id(self, server_id):

		status = True
		files = []

		try:
			files = self.db.table('ipfs_files').where('server_id', server_id).get()
		except Exception as err:
			log.error(err)
			status = False

		return (status, files)

	def unset_files_by_server(self, id):

		status = True

		try:
			self.db.table('ipfs_files').where('server_id', id).update({'server_id' : 0, 'hash' : '' })
		except Exception as err:
			log.error(err)
			status = False

		return status

	def mark_file_for_deletion(self, file_id):

		status = True

		try:
			self.db.table('ipfs_files').where('id', file_id).update({"is_active" : INACTIVE })
		except Exception as err:
			log.error(err)
			status = False

		return status

	def get_file_for_upload(self):

		status = True
		file = None

		try:
			file = self.db.table('ipfs_files').where('is_active', ACTIVE).where('upload_status',PENDING).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, file)

	def get_file_for_deletion(self):

		status = True
		file = None

		try:
			file = self.db.table('ipfs_files').where('is_active', INACTIVE).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, file)
		
	def register_ipns_key(self, params):
		
		status = True
		id = None

		try:
			id = self.db.table('ipns_keys').insert_get_id(params)
		except Exception as err:
			log.error(err)
			status = False

		return (status, id)
		
	def delete_key(self, id):
		status = True

		try:
			self.db.table('ipns_keys').where('id', id).delete()
		except Exception as err:
			log.error(err)
			status = False

		return status	
		
	def get_ipns_key(self, id):
		
		status = True
		rec = None

		try:
			rec = self.db.table('ipns_keys').where('id', id).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, rec)
		
	def get_ipns_key_by_name(self, key):
		
		status = True
		rec = None

		try:
			rec = self.db.table('ipns_keys').where('key', key).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, rec)

	
	def mark_key_for_deletion(self, key_id):

		status = True

		try:
			self.db.table('ipns_keys').where('id',key_id).update({"is_active" : INACTIVE })
		except Exception as err:
			log.error(err)
			status = False

		return status
		
	def get_key_for_deletion(self):

		status = True
		key = None

		try:
			key = self.db.table('ipns_keys').where('is_active', INACTIVE).first()
		except Exception as err:
			log.error(err)
			status = False

		return (status, key)

	def get_ipns_keys(self, start_index, chunk):

		status = True
		keys = []

		try:
			keys = self.db.table('ipns_keys').offset(start_index).limit(chunk).get()
		except Exception as err:
			log.error(err)
			status = False

		return (status, keys)
		
	def reset_all_tables(self):
		
		status = True
		keys = []

		try:
			self.db.table('ipfs_servers').delete()
			self.db.table('ipfs_files').delete()
			self.db.table('ipns_keys').delete()
			self.db.table('sqlite_sequence').where('name','ipfs_servers').delete()
			self.db.table('sqlite_sequence').where('name','ipfs_files').delete()
			self.db.table('sqlite_sequence').where('name','ipns_keys').delete()
		except Exception as err:
			log.error(err)
			status = False

		return status
		
	def get_sum_file_size_by_server(self, server_id):
		
		status = True
		total_size = 0
		
		try:
			total_size = self.db.table('ipfs_files').where('server_id',server_id).sum('size')
		except Exception as err:
			log.error(err)
			status = False

		if total_size == None:
			total_size = 0
		
		return (status, total_size)
		
		
		
		



