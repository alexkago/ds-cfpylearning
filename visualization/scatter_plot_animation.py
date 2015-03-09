import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import redis
import json
import pickle

class PolygonHandler:
    # Constructor
    def __init__(self):
        self.numberPoints = 100
        self.X = [0] * self.numberPoints
        self.Y = [0] * self.numberPoints
        self.line_x = np.arange(-5, 5, 0.01)

        self.fig , ax = plt.subplots()
        self.sc = ax.scatter(self.X,self.Y)
        self.line, = ax.plot(self.line_x, 0*self.line_x)
        ax.set_xlim(-5,5)
        ax.set_ylim(-5,5)

        self.data_key = 'test_model1_data'
        self.model_key = 'test_model1_object'

        DB_HOST = 'localhost'
        DB_PORT = 6379
        DB_PW = ''
        REDIS_DB = 1

        self.r = redis.StrictRedis(host=DB_HOST,
                                  port=DB_PORT,
                                  password=DB_PW,
                                  db=REDIS_DB)

    # Print the polygon
    def update(self,_):
        print "polling data..."
        data_available = self.r.llen(self.data_key)
        data = self.r.lrange(self.data_key,
                             data_available-self.numberPoints,
                             data_available)

        dict_data = [json.loads(el) for el in data]
        for i in range(len(dict_data)):
            self.X[i] = dict_data[i]['input']
            self.Y[i] = dict_data[i]['label']

        self.sc.set_offsets(np.column_stack((self.X,self.Y)))

        pickled_mdl = self.r.get(self.model_key)
        mdl = pickle.loads(pickled_mdl)
        params = mdl.get_parameters()
        print params


        self.line.set_data(self.line_x, self.line_x*params['input']+params['constant'])
        return self.sc, self.line,

P = PolygonHandler()
ani = animation.FuncAnimation(P.fig, P.update, interval=200, blit=False)

plt.show()
