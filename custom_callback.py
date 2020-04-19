# Class to take the iteration time for each 10 iterations

import keras
from keras.callbacks import Callback
import time

class CountTime(Callback):
	def __init__(self,
			final_time = 0.0,
			init_time = 0.0,
			init_time_per_step = 0.0,
			count=1,
			first_two = True,
			val_init_time = 0.0,
			first_valid = True):
	
		self.count = count
		self.final_time = final_time
		self.init_time = init_time
		self.init_time_per_step = init_time_per_step
		self.first_two = first_two
		self.val_init_time = val_init_time
		self.first_valid = first_valid

	def on_train_batch_begin(self, batch, logs=None):
		if self.count == 11:
			self.final_time = time.time() - self.init_time
			print('\n10 steps training: {}s'.format(self.final_time))
			print('\nReal time: {}'.format(time.time()))
			self.count = 1

		if self.count == 1:
			self.init_time = time.time()

		if self.first_two: 
			if self.count > 1:
				print('\nStep {} : {}s'.format(self.count-1, time.time()-self.init_time_per_step))
				if self.count > 2:
					self.first_two = False
			self.init_time_per_step = time.time()				

		self.count = self.count + 1

	def on_epoch_begin(self, epoch, logs=None):
		self.first_two = True
		self.count = 1
			

	def on_epoch_end(self, epoch, logs=None):
		self.final_time = time.time() - self.init_time
		print('\n{} steps training: {}s'.format(self.count-1, self.final_time))

		validation_time = time.time() - self.val_init_time
		print("Validation time: {}".format(validation_time))
		print('\nReal time: {}'.format(time.time()))
		self.first_valid = True



	def on_test_batch_begin(self, batch, logs=None):

		"""Called at the beginning of a batch in `evaluate` methods.

		Also called at the beginning of a validation batch in the `fit` methods,
		if validation data is provided.

		Subclasses should override for any actions to run.

		# Arguments
			batch: integer, index of batch within the current epoch.
			logs: dict, has keys `batch` and `size` representing the current
				batch number and the size of the batch.
		"""

		if self.first_valid:

			self.val_init_time = time.time()
			self.first_valid = False
		
