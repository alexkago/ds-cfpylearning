import os
import json
import redis
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# set up redis service, check previously if we're running locally by checking for env variable
if os.environ.get('VCAP_SERVICES') is None:
    r = redis.Redis(host='localhost', port=6379, password='')
else:
    rediscloud_service = json.loads(os.environ['VCAP_SERVICES'])['rediscloud'][0]
    credentials = rediscloud_service['credentials']
    r = redis.Redis(host=credentials['hostname'], port=credentials['port'], password=credentials['password'])

# get port where this app should run on
# in case we run locally it doesn't exist - then just run it on 8080
port = int(os.getenv("VCAP_APP_PORT", 8080))

# initialize values in redis
if r.get('counter') is None:
    r.set('counter',0)


# define routes
@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/test', methods=['POST'])
def test():
    print request.json
    return jsonify({"data": str(request.json)}), 201

@app.route('/createModel/<modelname>', methods=['POST'])
def createModel(modelname):
    if request.json['modelname'] is None:
        print "modelname field is missing"
        abort(500)

    r.lpush('models', request.json['modelname'])
    return jsonify({"model": str(request.json)}), 201

@app.route('/dataInput', methods=['POST'])
def dataInput():
    if request.json['modelname'] is None:
        print "modelname field is missing"
        abort(500)

    data = request.json
    key = modelname+'_data_'+r.get('counter')
    r.set(key, data)
    r.incr('counter')
    return str(data) + " added at " + key + "\n"


# run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port), debug=True)
