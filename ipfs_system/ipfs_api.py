import simplejson as json
import os
import io
import logging

from flask import Flask, make_response, request
from ipfs_manager import *

log = logging.getLogger(__name__)

manager = IPFSManager()
app = Flask(__name__)

@app.route("/")
def index():
	return "SCL IPFS SYSTEM SERVICES"

@app.route("/api/ipfs/server",methods=["POST"])
def create_server():
	
	log.info("CREATE SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		params = {}

		for key in request.form:
			if key in ["directory","tag","swarm_port","api_port","gateway_port","max_dir_size"]:
				params[key] = request.form[key]
			
		if "swarm_port" not in request.form:
			params["swarm_port"] = 0
			
		if "api_port" not in request.form:
			params["api_port"] = 0
			
		if "gateway_port" not in request.form:
			params["gateway_port"] = 0	
			
		if "max_dir_size" not in request.form:
			params["gateway_port"] = 100
			
		status, server = manager.register_server(params)

		if server:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = server.serialize()
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/all",methods=["GET"])
def get_servers():
	
	log.info("GET SERVERS")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		page =  request.args.get('page', 1, int)
		records =  request.args.get('records', 10, int)

		status, servers = manager.get_servers(page,records)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = servers.all()
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = []
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/<int:id>",methods=["PUT"])
def update_server(id):
	
	log.info("UPDATE SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		params = {}

		for key in request.form:
			if key in ["tag","swarm_port","api_port","gateway_port","max_dir_size","is_private"]:
				params[key] = request.form[key]
		
		status, server, pid = manager.update_server(id, params)

		if server:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = server.serialize()
			resp_data["data"]["pid"] = pid
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/<int:id>",methods=["DELETE"])
def delete_server(id):
	
	log.info("DELETE SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status = manager.delete_server(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/<int:id>/start",methods=["PUT"])
def start_server(id):
	
	log.info("START SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status, pid = manager.start_server(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
			resp_data["data"]["pid"] = pid
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/<int:id>/restart",methods=["PUT"])
def restart_server(id):
	
	log.info("RESTART SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status, pid = manager.restart_server(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
			resp_data["data"]["pid"] = pid
			resp = make_response(json.dumps(resp_data), 200)
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		resp = make_response(json.dumps(resp_data), 400)

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/<int:id>/stop",methods=["PUT"])
def stop_server(id):
	
	log.info("STOP SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status = manager.stop_server(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
		else:
			raise Exception("")

	except Exception as err:

		resp_data = {}
		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/server/<int:id>/ping",methods=["GET"])
def ping_server(id):
	
	log.info("PING SERVER")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status = manager.ping_server(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/file",methods=["POST"])
def upload_file():
	
	log.info("UPLOAD FILE")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		params = {}

		for key in request.form:
			params[key] = request.form[key]

		status, id = manager.upload_file(params)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
			resp_data["data"]["id"] = id
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/file/all",methods=["GET"])
def get_files():
	
	log.info("GET FILES")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		page =  request.args.get('page', 1, int)
		records =  request.args.get('records', 10, int)

		status, files = manager.get_files(page,records)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = files.all()
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = []
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipfs/file/<int:id>",methods=["DELETE"])
def delete_file(id):
	
	log.info("DELETE FILE")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status = manager.delete_file(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipns/key",methods=["POST"])
def create_ipns_key():
	
	log.info("CREATE IPNS KEY")
	
	resp = None
	resp_data = {}
	status_code = 200

	try:
		
		key = request.form["key"]
		server_id = request.form["server_id"]
		
		params = {}
		params["key"] = key
		params["server_id"] = server_id
		
		status, key_rec = manager.create_ipns_key(params)
		
		if key_rec:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = key_rec.serialize()
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp
	
	
@app.route("/api/ipns/key/all",methods=["GET"])
def get_ipns_keys():
	
	log.info("GET KEYS")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		page =  request.args.get('page', 1, int)
		records =  request.args.get('records', 10, int)

		status, keys = manager.get_ipns_keys(page,records)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = keys.all()
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = []
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp
	
	
@app.route("/api/ipns/publish",methods=["POST"])
def publish_key():
	
	log.info("PUBLISH KEY")
	
	resp = None
	resp_data = {}
	status_code = 200

	try:		
		key_id = request.form["key_id"]
		file_id = request.form["file_id"]
		ttl = request.form["ttl"]
		
		params = {}
		params["key_id"] = key_id
		params["file_id"] = file_id
		params["ttl"] = "%sh" % ttl
		
		status, file = manager.publish_key(params)
		
		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = file
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp

@app.route("/api/ipns/key/<int:id>",methods=["DELETE"])
def delete_ipns_key(id):
	
	log.info("DELETE IPNS KEY")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		status = manager.delete_ipns_key(id)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp
	
	
@app.route("/api/ipns/file",methods=["GET"])
def download_ipns_file():
	
	log.info("DOWNLOAD FILE BY IPNS")
	
	def generate(fp):
		
		with open(fp,"rb") as f:
			
			while True:
				chunk = f.read(io.DEFAULT_BUFFER_SIZE)
				if not chunk:
					break
				yield chunk
				
		os.remove(fp)

	resp = None
	resp_data = {}
	status_code = 200

	try:

		ipns_hash = request.args.get('hash')
		file_name =  request.args.get('filename')
		
		status, temp_file = manager.download_ipns_file(ipns_hash)
		
		if status:
			resp = app.response_class(generate(temp_file))
			resp.headers.set('Content-Disposition', 'attachment', filename=file_name)
		else:
			raise Exception("")
		
	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = {}
		status_code = 400

		resp = make_response(json.dumps(resp_data), status_code)

	return resp	
	
@app.route("/api/ipfs/server/<int:id>/test",methods=["GET"])
def is_enough_storage(id):
	
	log.info("TEST FOR STORAGE AVAILABILITY")

	resp = None
	resp_data = {}
	status_code = 200

	try:
		fqfp =  request.args.get("fqfp", None)
		server_id = id
		
		params = {}
		params["fqfp"] = fqfp
		params["server_id"] = server_id

		status = manager.is_enough_storage(params)

		if status:
			resp_data["status"] = "SUCCESS"
			resp_data["data"] = {}
		else:
			raise Exception("")

	except Exception as err:

		resp_data["status"] = "FAILED"
		resp_data["data"] = []
		status_code = 400

	resp = make_response(json.dumps(resp_data), status_code)

	return resp


