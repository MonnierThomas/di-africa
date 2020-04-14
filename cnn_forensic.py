# -*- coding: utf-8 -*-
"""
Data must be prepared and sorted in 2 classes {'G','O'} which are 
separated into 3 folders {'Train', 'Validate', 'Test'}, before applying CNN method.
Such can be done using creation_data.py and prepare_data.py.
As input, we use CWT.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from tensorflow.keras import optimizers, layers
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix

train_dir = "C:/Users/MIG/Desktop/cnntrain/traindata/train"
valid_dir = "C:/Users/MIG/Desktop/cnntrain/traindata/validate"
test_dir = "C:/Users/MIG/Desktop/cnntrain/traindata/test"
save_dir = ""

#MODEL PARAMETERS
batch_size = 20
IMG_HEIGHT, IMG_WIDTH = 50, 200
total_val = 1106
epochs = 20
total_train = 3891


def data_preparation(train_dir = train_dir, valid_dir = valid_dir):
	"""Formats the image into appropriately pre-processed floating point tensors before feeding to the network"""
	train_image_generator = ImageDataGenerator(rescale=1./255)
	validation_image_generator = ImageDataGenerator(rescale=1./255)
	test_image_generator = ImageDataGenerator(rescale=1./255)
	train_data_gen = train_image_generator.flow_from_directory(batch_size=batch_size,
															   directory=train_dir,
															   shuffle=True,
															   target_size=(IMG_HEIGHT, IMG_WIDTH),
															   class_mode='categorical')
	valid_data_gen = train_image_generator.flow_from_directory(batch_size=batch_size,
															   directory=valid_dir,
															   shuffle=True,
															   target_size=(IMG_HEIGHT, IMG_WIDTH),
															   class_mode='categorical')
	return train_data_gen, valid_data_gen
  

def model_creation():
	"""Computes the model, using Keras'CNN."""
	model = Sequential()

	model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)))
	model.add(MaxPooling2D((2, 2)))
	model.add(Conv2D(32, (3, 3), activation='relu'))
	model.add(MaxPooling2D((2, 2)))
	model.add(Flatten())

	model.add(Dense(64, activation='relu'))
	model.add(Dense(64, activation='relu'))
	model.add(Dense(2, activation='softmax'))


	EDCE = optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False)

	model.compile(optimizer=EDCE,
				  loss='binary_crossentropy',
				  metrics=['accuracy'])
	return model


def model_training(model, train_data_gen, valid_data_gen):
	"""Trains the model"""

	history = model.fit_generator(train_data_gen,
								steps_per_epoch=total_train // batch_size,
								epochs=epochs,
								validation_data=valid_data_gen,
								validation_steps=total_val // batch_size)
	accu = model.evaluate_generator(train_data_gen)
	print(accu)

	return history


def model_saving(model, save_dir = save_dir):
	"""Saves the model"""

	model_json = model.to_json() # serialize model to JSON
	with open("model.json", "w") as json_file:
		json_file.write(model_json)
	
	model.save_weights(save_dir+"model.h5") # serialize weights to HDF5
	print("Saved model to disk")
	return 0


def model_loading(save_dir = save_dir):
	"""Loads the model"""

	json_file = open('model.json', 'r') # load json and create model
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = tf.keras.models.model_from_json(loaded_model_json)
	
	loaded_model.load_weights("model.h5") # load weights into new model
	print("Loaded model from disk")
	return loaded_model


def prediction(model, test_dir = test_dir):
	"""Tests the previous and trained model and returns prediction probalities"""
	test_image_generator = ImageDataGenerator(rescale=1./255)
	test_data_gen = test_image_generator.flow_from_directory(batch_size=batch_size,
														  directory=test_dir,
														  shuffle=False,
														  target_size=(IMG_HEIGHT, IMG_WIDTH),
														  class_mode='categorical')
	predic = model.predict_generator(test_data_gen, 
									 steps=None, 
									 callbacks=None, 
									 max_queue_size=10, 
									 workers=1, 
									 use_multiprocessing=False, 
									 verbose=1)
	accu = model.evaluate_generator(test_data_gen)
	print(accu)
	return predic, test_data_gen


def conf_matrix(predic, classes):
	"""Returns confusion matrix"""
	pred = [np.argmax(i) for i in predic]
	cm = confusion_matrix(classes, pred)
	return cm


def info_plotting(cm, history):
	fig, ax = plt.subplots()
	print(cm)
	im = ax.imshow(cm, interpolation='nearest', cmap = plt.cm.Blues)
	ax.figure.colorbar(im, ax=ax)
	plt.show()
	
	# Plot training & validation accuracy values
	plt.plot(history.history['accuracy'])
	plt.plot(history.history['val_accuracy'])
	plt.title('Model accuracy')
	plt.ylabel('Accuracy')
	plt.xlabel('Epoch')
	plt.legend(['Train', 'Validate'], loc='lower right')
	plt.show()


	# Plot training & validation loss values
	plt.plot(history.history['loss'])
	plt.plot(history.history['val_loss'])
	plt.title('Model loss')
	plt.ylabel('Loss')
	plt.xlabel('Epoch')
	plt.legend(['Train', 'Validate'], loc='lower right')
	plt.show()

	return 0


def main ():
	global history
	train_data_gen, valid_data_gen = data_preparation()
	model = model_creation()
	history = model_training(model, train_data_gen, valid_data_gen)
	model.summary()
	model_saving(model)
	predic, test_data_gen = prediction(model)
	cm = conf_matrix(predic, test_data_gen.classes)
	info_plotting(cm, history)

	return 0

if __name__=="__main__":
	 main()









from keras.utils import plot_model
plot_model(model, to_file='model.png')