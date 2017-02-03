import numpy as np
import geninput as INPUT
import gen_dataset as DATASET
from osgeo import gdal
import indices as INDICES
from skimage import io
from os import listdir
from sklearn.cluster import KMeans
from PIL import Image
import matplotlib.pyplot as plt
import dcapnet as DCAP
import mlpca as MLP
import scipy.ndimage
import scipy.misc
import sys
import metrics
from sklearn.linear_model import SGDRegressor
from sklearn.svm import SVR

def classify(R,V,Bt,Btnxt,model):
	shp=R.shape
	print 'Segmentation started'
	#P=MLP.predict(V)
	P = MLP.predict(V[:,27:36],V[:,0:27])
	#P = model.predict(V)
	print 'Segmentation complete'	
	C=np.zeros((shp[1],shp[2]))
	k=0
	for i in range(0,shp[1]):
		for j in range(0,shp[2]):
			if(R[0][i][j]>0):
				C[i][j] = P[k]
				k=k+1
	
	plt.imshow(np.transpose(C))
	plt.show()
	C = np.asarray(C>0,dtype = np.int32)

	Btd = np.asarray(Bt>0,dtype = np.int32)
	Btnxtd = np.asarray(Btnxt>0,dtype = np.int32)
	print metrics.change_metric(R,Btd,Btnxtd,C)
	C=np.transpose(C)
	np.save('Classified.npy',C)
	

def viz_layer1(R,V):
	shp = R.shape
	P = DCAP.layer1(V)
	C = np.zeros((shp[1],shp[2]))
	for l in range(P.shape[1]):
		k = 0
		N = P[:,l].reshape([-1,1])
		#clus_P = KMeans(n_clusters=5, random_state=0).fit(N).labels_
		for i in range(0,shp[1]):
			for j in range(0,shp[2]):
				if(R[0][i][j]>0):
					C[i][j] = N[k][l]
					k = k+1
		plt.imshow(np.transpose(C))
		plt.show()

def viz_layer2(R,V):
	shp=R.shape
	P=DCAP.layer2(V)
	for l in range(0,P.shape[1]):
		N = P[:,1].reshape([-1,1])		
		clus_P = KMeans(n_clusters=3, random_state=0).fit(N).labels_
		C=np.zeros((shp[1],shp[2]))
		k=0
		for i in range(0,shp[1]):
			for j in range(0,shp[2]):
				if(R[0][i][j]>0):
					C[i][j] = clus_P[k]+1				
					k=k+1
		plt.imshow(np.transpose(C))
		plt.show()
	

def run(R,Bt,Btnxt,Btnxtnxt, generate = False):
	wx=3
	wy=3
	shp=R.shape
	print 'Training set generation started'	
	if generate:
		trX, trY, teX, teY, V, B = DATASET.dcap_dataset(R,Bt,Btnxt,wx,wy)
		np.save('./dataset/DCAP_trX.npy',trX)
		np.save('./dataset/DCAP_trY.npy',trY)
		np.save('./dataset/DCAP_teX.npy',teX)
		np.save('./dataset/DCAP_teY.npy',teY)
		np.save('./dataset/DCAP_V.npy',V)
		np.save('./dataset/DCAP_B.npy',B)
	else:
		trX = np.load('./dataset/DCAP_trX.npy')
		trY = np.load('./dataset/DCAP_trY.npy')
		teX = np.load('./dataset/DCAP_teX.npy')
		teY = np.load('./dataset/DCAP_teY.npy')
		V = np.load('./dataset/DCAP_V.npy')
		B = np.load('./dataset/DCAP_B.npy')
	
	print 'Dimension of input : ', len(trX[0])
	print 'Training set size : ', trX.shape[0]

	print 'Training set generation ended'
	
	if(wx!=3 or wy!=3):
		print 'Window size has to be 3X3'
		return
	
	#DCAP.fit(trX, trY, B, epoch = 20, batch_size = 1000, early_stop=True)
	trX = trX.reshape([trX.shape[0],36])
	V = V.reshape([V.shape[0],36])
	
	#model = SVR()
	#model.fit(trX,trY)
	MLP.fit(trX,trY, B, epoch = 50, batch_size = 1000, early_stop=True,epsilon = 0.012)
	
	classify(R,V,Bt,Btnxt,None)
	exit()
	V = DATASET.create_test_dataset(R,Btnxt,Btnxtnxt)
	classify(R,V,Bt,Btnxt,None)
	

if __name__ == "__main__":
	raw_loc='/home/ubuntu/workplace/saptarshi/Data/raw/mumbai/'
	label_loc='/home/ubuntu/workplace/saptarshi/Data/labelled/mumbai/'
	
	R = INPUT.give_raster(raw_loc + '1990.tif')
	Bt = INPUT.give_raster(label_loc + 'cimg1996.tif')[0]
	Btnxt = INPUT.give_raster(label_loc + 'cimg2000.tif')[0]
	Btnxtnxt = INPUT.give_raster(label_loc + 'cimg2010.tif')[0]
	
	
	'''R = R[:,286:783,345:802]
	Bt = Bt[286:783,345:802]
	Btnxt = Btnxt[286:783,345:802]
	Btnxtnxt = Btnxtnxt[286:783,345:802]'''
	
	Bt = Bt/255
	Btnxt = Btnxt/255
	Btnxtnxt = Btnxtnxt/255
	
	
	Bt,Btnxt = DATASET.ageBuiltUp(R,Bt,Btnxt,0.1,first = True)
	
	Btnxt,Btnxtnxt = DATASET.ageBuiltUp(R,Btnxt,Btnxtnxt,0.1,first=False)
	
	
	run(R,Bt,Btnxt,Btnxtnxt,generate = False)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
