import tensorflow as tf
import numpy as np

class DynamicRNNAE:
	def __init__(self, sml = 53, nfeatures = 1, tsteps = 30):
		# Parameters
		tf.reset_default_graph()
		self.learning_rate = 0.9
		self.momentum_rate = 0.1
		self.training_steps = tsteps
		self.batch_size = 100000
		self.display_step = 200

		# Network Parameters
		self.seq_max_len = sml # Sequence max length
		self.n_hidden = nfeatures # hidden layer num of features
		
		# tf Graph input
		self.x = tf.placeholder("float", [None,self.seq_max_len,1])	
		self.y = tf.placeholder("float", [None,self.seq_max_len,1])
		# A placeholder for indicating each sequence length
		self.seqlen = tf.placeholder("int32", [None])
		
		self.weights = {'out': tf.Variable(tf.random_normal([self.n_hidden,1]))}
		self.biases = {'out': tf.Variable(tf.random_normal([1]))}
		
		x_list = tf.unstack(self.x, self.seq_max_len, 1)
		y_list = tf.unstack(self.y, self.seq_max_len, 1)
		
		with tf.variable_scope('lstm1_x'):
			encoder_x = tf.contrib.rnn.BasicLSTMCell(self.n_hidden)
			self.outputs_enc_x, states = tf.contrib.rnn.static_rnn(encoder_x, x_list, dtype=tf.float32, sequence_length = self.seqlen)
		
		with tf.variable_scope('lstm1_y'):
			encoder_y = tf.contrib.rnn.BasicLSTMCell(self.n_hidden)
			self.outputs_enc_y, states = tf.contrib.rnn.static_rnn(encoder_y, y_list, dtype=tf.float32, sequence_length = self.seqlen)
		
		#Encoded features of x
		self.outputs_enc_x = tf.stack(self.outputs_enc_x)
		self.outputs_enc_x = tf.transpose(self.outputs_enc_x, [1, 0, 2])
		batch_size_x = tf.shape(self.outputs_enc_x)[0]
		index_x = tf.range(0, batch_size_x) * self.seq_max_len + (self.seqlen - 1)
		self.outputs_enc_x = tf.gather(tf.reshape(self.outputs_enc_x, [-1, self.n_hidden]), index_x)
		
		enc_rep_x = tf.matmul(self.outputs_enc_x, self.weights['out']) + self.biases['out']
		enc_rep_x = tf.tile(tf.reshape(enc_rep_x, [-1,1,1]), multiples = (1,self.seq_max_len,1))
		enc_rep_x = tf.unstack(enc_rep_x, self.seq_max_len, 1)
		
		#Encoded features of y
		self.outputs_enc_y = tf.stack(self.outputs_enc_y)
		self.outputs_enc_y = tf.transpose(self.outputs_enc_y, [1, 0, 2])
		batch_size_y = tf.shape(self.outputs_enc_y)[0]
		index_y = tf.range(0, batch_size_y) * self.seq_max_len + (self.seqlen - 1)
		self.outputs_enc_y = tf.gather(tf.reshape(self.outputs_enc_y, [-1, self.n_hidden]), index_y)
		
		self.outputs_enc = tf.concat([self.outputs_enc_x, self.outputs_enc_y], 1)
		
		enc_rep_y = tf.matmul(self.outputs_enc_y, self.weights['out']) + self.biases['out']
		enc_rep_y = tf.tile(tf.reshape(enc_rep_y, [-1,1,1]), multiples = (1,self.seq_max_len,1))
		enc_rep_y = tf.unstack(enc_rep_y, self.seq_max_len, 1)
		
		with tf.variable_scope('lstm2_x'):
			decoder_x = tf.contrib.rnn.BasicLSTMCell(1)
			self.outputs_dec_x, states = tf.contrib.rnn.static_rnn(decoder_x, enc_rep_x, dtype=tf.float32, sequence_length=self.seqlen)
		
		with tf.variable_scope('lstm2_y'):		
			decoder_y = tf.contrib.rnn.BasicLSTMCell(1)
			self.outputs_dec_y, states = tf.contrib.rnn.static_rnn(decoder_y, enc_rep_y, dtype=tf.float32, sequence_length=self.seqlen)
		
		self.outputs_dec_x = tf.stack(self.outputs_dec_x)
		self.outputs_dec_x = tf.transpose(self.outputs_dec_x, [1, 0, 2])
		
		self.outputs_dec_y = tf.stack(self.outputs_dec_y)
		self.outputs_dec_y = tf.transpose(self.outputs_dec_y, [1, 0, 2])

		mse = tf.losses.mean_squared_error(labels = self.x, predictions = self.outputs_dec_x) + tf.losses.mean_squared_error(labels = self.y, predictions = self.outputs_dec_y) 
		self.cost = tf.reduce_mean(mse)
		#self.optimizer = tf.train.GradientDescentOptimizer(learning_rate = self.learning_rate).minimize(self.cost)
		self.optimizer = tf.train.MomentumOptimizer(learning_rate = self.learning_rate, momentum = self.momentum_rate, use_nesterov= True).minimize(self.cost)
		self.sess = tf.Session()
		init = tf.global_variables_initializer()
		self.sess.run(init)
	
	def run_dynamic_rnn(self, X, Y, S):
		mse = []
		
		X_part = X[S>=30]
		Y_part = Y[S>=30]
		S_part = S[S>=30]
		
		for i in range(0,500):
			self.sess.run(self.optimizer, feed_dict = {self.x: X_part, self.y: Y_part, self.seqlen: S_part})
		
		for i in range(0,self.training_steps):
			for j in range(0,X.shape[0], self.batch_size):
				batch_x = X[j:min(j+self.batch_size, X.shape[0]),:,:]
				batch_y = Y[j:min(j+self.batch_size, Y.shape[0]),:,:]
				batch_s = S[j:min(j+self.batch_size, S.shape[0])]				
				self.sess.run(self.optimizer, feed_dict = {self.x: batch_x, self.y: batch_y, self.seqlen: batch_s})
			e = self.sess.run(self.cost, feed_dict = {self.x: X, self.y: Y, self.seqlen: S})
			#print e 
			mse.append(e)
		
		return mse
	
	def get_encoded_features(self, X, Y, S):
		return self.sess.run(self.outputs_enc, feed_dict={self.x: X, self.y: Y, self.seqlen: S})
	
	def get_decoded_features(self, X, Y, S):
		x = self.sess.run(self.outputs_dec_x, feed_dict={self.x: X, self.seqlen: S})
		y = self.sess.run(self.outputs_dec_y, feed_dict={self.y: Y, self.seqlen: S})
		return x,y
		
if __name__ == '__main__':
	rnn = DynamicRNNAE()
	X = np.array([[i for i in range(0,36)]])
	S = np.random.randint(10, size = (1,))
	X = X.reshape([1,-1,1])/np.max(np.ndarray.flatten(X))
	rnn.run_dynamic_rnn(X, S)
	
	
	
	
	
	
