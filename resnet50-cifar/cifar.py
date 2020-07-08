"""ResNet model for classifying images from CIFAR-10 dataset.

Support single-host training with one or multiple devices.

ResNet as proposed in:
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
Deep Residual Learning for Image Recognition. arXiv:1512.03385

CIFAR-10 as in:
http://www.cs.toronto.edu/~kriz/cifar.html


"""
import argparse 
import tensorflow as tf
import custom_callback
import time

init_time = time.time()
#newInput = tf.keras.layers.InputLayer(input_shape=(0,32,32,3))
#newOutputs = model(newInput)
#newModel = Model(newInput, newOutputs)
parser = argparse.ArgumentParser()
parser.add_argument("--batch-size",type=int)
parser.add_argument("--epochs",type=int)
args = parser.parse_args()
batch_size = args.batch_size
epochs = args.epochs

(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()

# Normalize pixel values to be between 0 and 1
train_images, test_images = train_images / 255.0, test_images / 255.0


mirrored_strategy = tf.distribute.MirroredStrategy()
with mirrored_strategy.scope():
	model = tf.keras.applications.ResNet50(include_top=False, input_shape=(32, 32, 3))
	model.summary()
	model.compile(optimizer='adam',
		loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
		metrics=['accuracy'])

count_time = custom_callback.CountTime()
epoch_time = custom_callback.EpochTime()
print("Tempo de Inicializacao:", time.time() - init_time)
fit_time_init = time.time()
history = model.fit(train_images, train_labels, batch_size=batch_size, epochs=epochs, 
					validation_data=(test_images, test_labels),
					callbacks = [count_time, epoch_time])
print("Tempo do fit:", time.time() - fit_time_init)
