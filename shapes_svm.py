import pandas as pd
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm

import pickle

path = os.getcwd() + '/my.csv'
data = pd.read_csv(path, header=None, names=["hu1", 'hu2', 'hu3', 'hu4', 'hu5', 'hu6', 'hu7', 'class'])
data = data.iloc[1:]
data.head()

normalized = data[["hu1", 'hu2', 'hu3', 'hu4', 'hu5', 'hu6', 'hu7']].astype(float)

Y = data['class'].values.astype(float)
X = normalized[["hu1", 'hu2', 'hu3', 'hu4', 'hu5', 'hu6', 'hu7']].astype(float).to_numpy()

clf = svm.SVC(kernel='rbf', probability=True, gamma=0.1)

clf.fit(X, Y)

print(X[0])
print(clf.predict_proba([X[0]]))

result = clf.score(X, Y)
print(result)

"""svm = cv2.ml.SVM_create()
svm.setType(cv2.ml.SVM_C_SVC)
svm.setKernel(cv2.ml.SVM_LINEAR)
svm.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER, 10000, 1e-6))

svm.train(X, cv2.ml.ROW_SAMPLE, Y)
"""
# Data for visual representation
"""width = 512
height = 512
image = np.zeros((height, width, 3), dtype=np.uint8)
# Show the decision regions given by the SVM
green = (0, 255, 0)
blue = (255, 0, 0)
for i in range(image.shape[0]):
    for j in range(image.shape[1]):
        sampleMat = np.matrix([[j, i]], dtype=np.float32)
        response = svm.predict(sampleMat)[1]
        if response == 1:
            image[i, j] = green
        elif response == -1:
            image[i, j] = blue
# Show the training data
thickness = -1
cv2.circle(image, (501, 10), 5, (0, 0, 0), thickness)
cv2.circle(image, (255, 10), 5, (255, 255, 255), thickness)
cv2.circle(image, (501, 255), 5, (255, 255, 255), thickness)
cv2.circle(image, (10, 501), 5, (255, 255, 255), thickness)
# Show support vectors
thickness = 2
sv = svm.getUncompressedSupportVectors()
for i in range(sv.shape[0]):
    cv2.circle(image, (int(sv[i, 0]), int(sv[i, 1])), 6, (128, 128, 128), thickness)
cv2.imwrite('result.png', image)  # save the image
cv2.imshow('SVM Simple Example', image)  # show it to the user
cv2.waitKey()"""

pickle.dump(clf, open('shapes_svm.sav', 'wb'))

loaded_model = pickle.load(open('shapes_svm.sav', 'rb'))
result = loaded_model.score(X, Y)
print("score", result)
