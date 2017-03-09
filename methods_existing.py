import numpy as np
import geninput as INPUT
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from matplotlib import cm
import sklearn.tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from RBFN import RBF
import time
import run
from sklearn.model_selection import cross_val_score

def method_fit(trX,trY):	
	#model = SGDClassifier()
	#model = DecisionTreeClassifier()
	#model = RandomForestClassifier()
	#model = MLPClassifier()
	#model = AdaBoostClassifier()
	#model = RBF(trX.shape[1],10,1)
	model = SVC()
	
	scores = cross_val_score(model,trX,trY,cv=10)
	print("Accuracy: %f (+/- %f)" % (scores.mean(), scores.std() * 2))
	#model = GaussianNB()
	start = time.time()
	model.fit(trX,trY)
	print time.time()-start
	#sklearn.tree.export_graphviz(model, out_file = 'ca_Decision_tree.dot', max_depth=5)
	#exit()
	return model
	
if __name__ =="__main__":
	data_folder = './dataset/'
	raw_loc='/home/ubuntu/workplace/saptarshi/Data/raw/mumbai/'
	label_loc='/home/ubuntu/workplace/saptarshi/Data/labelled/mumbai/'
	
	R = INPUT.give_raster(raw_loc + '1990.tif')
	Bt = INPUT.give_raster(label_loc + 'cimg1996.tif')[0]
	Btnxt = INPUT.give_raster(label_loc + 'cimg2000.tif')[0]
	Btnxtnxt = INPUT.give_raster(label_loc + 'cimg2010.tif')[0]
	
	Bt = Bt/255
	Btnxt = Btnxt/255
	Btnxtnxt = Btnxtnxt/255
	
	trX = np.load(data_folder+'trainX.npy')[:,5:]
	trY = np.load(data_folder+'DCAP_trY.npy')
	B = np.load(data_folder +'DCAP_B.npy')
	teX = np.load(data_folder+'testX.npy')[:,5:]
	
	trY[np.logical_and(trY>=0, B<0)] = 1
	trY[np.logical_and(trY>=0, B>=0)] = 2
	trY[np.logical_and(trY<=0, B<0)] = 0
	
	model = method_fit(trX,trY)
	
	run.classify(R,trX,Bt,Btnxt,model)
	run.classify(R,teX,Btnxt,Btnxtnxt,model)
	
