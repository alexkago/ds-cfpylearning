import os
from flask import Flask

app = Flask(__name__)

# set up redis service
rediscloud_service = json.loads(os.environ['VCAP_SERVICES'])['rediscloud'][0]
credentials = rediscloud_service['credentials']
r = redis.Redis(host=credentials['hostname'], port=credentials['port'], password=credentials['password'])

if r.get('counter') is None:
    r.set('counter',0)

# get port where this app should run on
port = int(os.getenv("VCAP_APP_PORT"))


# define routes
@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/createModel', methods=['POST'])
def createModel():
    jsondata = request.form['jsondata']
    data = json.loads(jsondata)
    return data

@app.route('/dataInput', methods=['POST'])
def jsonreq():
    jsondata = request.form['jsondata']
    data = json.loads(jsondata)
    key = 'data_'+r.get('counter')
    r.set(key, 'bar')
    r.incr('counter')
    return data + " added at " + key


# run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
