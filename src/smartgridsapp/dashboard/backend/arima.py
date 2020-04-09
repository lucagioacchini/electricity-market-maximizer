import pandas as pd 
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil import relativedelta
import numpy as np
from statsmodels.tsa.stattools import adfuller
import statsmodels.graphics.tsaplots as tplot
from statsmodels.tsa.arima_model import ARIMA
from influxdb import InfluxDBClient
from sklearn.metrics import mean_squared_error
import json
import warnings


with warnings.catch_warnings():
    warnings.filterwarnings("ignore")


#self.START = int(datetime.timestamp(self.START)*1e9)

H = 1

class ArimaV2():
    """For Genetic Analysis
    """
    def __init__(self, op, today):
        self.client = InfluxDBClient(
            'localhost', 
            8086, 
            'root', 
            'root', 
            'PublicBids'
        )
        self.op = op
        self.TODAY = today
        self.START = self.TODAY - relativedelta.relativedelta(days=60)
        self.TOMORROW = self.TODAY + relativedelta.relativedelta(days=1)

    def manageIndexTest(self, data):
        temp_date = pd.to_datetime(data['time'])
        data = (
            data
            .set_index(temp_date)
            .drop(columns=['time', 'OPS'])
        )
        idx = pd.date_range(self.START + relativedelta.relativedelta(days=1), self.TODAY)
        data.index = pd.DatetimeIndex(data.index.date)
        data = (data.reindex(idx, fill_value=0))
        
        return data

    def getDataTest(self, market):
        # Get the demand data from InfluxDB
        res = (
            self.client
            .query(
                f"SELECT * FROM demand{market} WHERE op='{self.op}' AND time >= '{self.START}'"
            )
            .raw
        )
        try:
            dem =(
                pd
                .DataFrame(
                    res['series'][0]['values'], 
                    columns = ['time', 'P', 'Q', 'OPS']
                )
            )
            dem = self.manageIndexTest(dem)
        except:
            dem = -1
        # Get the supply data from InfluxDB
        res = (
            self.client
            .query(
                f"SELECT * FROM supply{market} WHERE op='{self.op}' AND time >= '{self.START}'"
            )
            .raw
        )
        try:
            sup =(
                pd
                .DataFrame(
                    res['series'][0]['values'], 
                    columns = ['time', 'P', 'Q', 'OPS']
                )
            )
            sup = self.manageIndexTest(sup)
        except:
            sup = -1

        return dem, sup


    def runTest(self, data, label):
        X = data.values.astype('float32')
        
        model = ARIMA(
            X, 
            order=(0,1,0),
        )
        model_fit = model.fit(maxiter=200, disp=0, method='css')
        y = model_fit.forecast(H)[0][-1]
        
        if y < 0:
            y = 0
        return y 

    def predict(self):
        pred = []
        for m in ['MGP', 'MI', 'MSD']:
            # Get the demand and supply curves
            d, s = self.getDataTest(m)
            # If the operator is not active in the market, getData 
            # returns -1, so the same -1 is appended to theprediction 
            # and it is managed later by the genetic algorithm
            if isinstance(s, int):
                pred.append(-1.0)
                pred.append(-1.0)
            else:
                pred.append(self.runTest(s.P, f'{m}pO'))
                pred.append(self.runTest(s.Q, f'{m}qO'))
            # If the operator is not active in the market, getData 
            # returns -1, so the same -1 is appended to the prediction 
            # and it is managed later by the genetic algorithm            
            
            if isinstance(d, int):
                pred.append(-1.0)
                pred.append(-1.0)
            else:
                pred.append(self.runTest(d.P, f'{m}pD'))
                pred.append(self.runTest(d.Q, f'{m}qD'))
        
        return np.asarray(pred)