import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

import pickle

path = os.getcwd() + '/my_recznie.csv'
data = pd.read_csv(path, header=None, names=["hu1",'hu2','hu3','hu4','hu5','hu6','hu7','class'])
data = data.iloc[1:]
data.head()

normalized = data[["hu1",'hu2','hu3','hu4','hu5','hu6','hu7']].astype(float)

Y = data['class'].values.astype(float)
X = normalized[["hu1",'hu2','hu3','hu4','hu5','hu6','hu7']].to_numpy()

print(X)
exit()
logreg = LogisticRegression(max_iter=3050)
logreg.fit(X, Y)


print(logreg.score(X, Y))


pickle.dump(logreg, open('shapes.sav', 'wb'))

loaded_model = pickle.load(open('shapes.sav', 'rb'))
result = loaded_model.score(X, Y)
print(result)