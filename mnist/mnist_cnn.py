from __future__ import print_function
import keras
import time
from keras.datasets import mnist
from keras.models import Sequential
from keras.utils import multi_gpu_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import argparse 
from custom_callback import *
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--batch-size",type=int)
parser.add_argument("--num-gpus",type=int)
parser.add_argument("--epochs",type=int)
args = parser.parse_args()
batch_size = args.batch_size
num_gpus = args.num_gpus
epochs = args.epochs
num_classes = 10
# input image dimensions
img_rows, img_cols = 28, 28

# the data, split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

if K.image_data_format() == 'channels_first':
	x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
	x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
	input_shape = (1, img_rows, img_cols)
else:
	x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
	x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
	input_shape = (img_rows, img_cols, 1)

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
				 activation='relu',
				 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

#early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0.001, patience=100, verbose=0, mode='auto', baseline=None, restore_best_weights=False)
init_time = time.time()

count_time = CountTime()
epoch_time = EpochTime()
callbacks = [count_time, epoch_time]

if num_gpus == 1 or num_gpus == 0:
    model.compile(loss=keras.losses.categorical_crossentropy,
				optimizer=keras.optimizers.Adadelta(),
				metrics=['accuracy'])
    print("Initialization time", time.time() - init_time)
    model.fit(x_train, y_train,
			batch_size=batch_size,
			epochs=epochs,
			verbose=1,
			validation_data=(x_test, y_test),
		callbacks=callbacks)
else:
    new_model = multi_gpu_model(model, gpus=num_gpus)
    new_model.compile(loss=keras.losses.categorical_crossentropy,
				optimizer=keras.optimizers.Adadelta(),
				metrics=['accuracy'])
    print("Initialization time", time.time() - init_time)

    new_model.fit(x_train, y_train,
			batch_size=batch_size,
			epochs=epochs,
			verbose=1,
			validation_data=(x_test, y_test),
		callbacks=callbacks)

training_time = time.time() - init_time
print("Duracao do treinamento:", training_time)
score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
