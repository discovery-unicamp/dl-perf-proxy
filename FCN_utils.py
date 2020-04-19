# -*- coding: utf-8 -*-

import keras
from keras.models import Model, Sequential
from keras.layers import Dense, Activation, Dropout, Conv2D, MaxPooling2D, Flatten, Input
from keras.callbacks import ModelCheckpoint, EarlyStopping, Callback
from keras.utils import multi_gpu_model
from keras import optimizers, regularizers
import tensorflow
from custom_callback import *


def FCN_Lenet5(num_labels, keep_prob=1.0, weightsPath=None, img_shape=None):
   #Define o tamanho da entrada da rede
        input_img = Input(img_shape)
       
        #Define dimensoes da rede
        conv_filter_size = 5
        conv_filter_size_2 = 13
        pool_filter_size = 2
        depth_conv1 = 20
        depth_conv2 = 50
        depth_f1 = 500
        

        #Conv 1 + Pool 1
        x = Conv2D(depth_conv1, conv_filter_size, padding='valid', activation='relu', kernel_regularizer=regularizers.l2(0.0005), kernel_initializer='glorot_uniform')(input_img)
        x = MaxPooling2D(pool_size=pool_filter_size, strides=2, padding='valid')(x)
        
        #Conv 2 + Pool 2
        x = Conv2D(depth_conv2, conv_filter_size, activation='relu', kernel_regularizer=regularizers.l2(0.0005), kernel_initializer='glorot_uniform')(x)
        x = MaxPooling2D(pool_size=pool_filter_size, strides=2, padding='valid')(x)
        
        #FC 1 + Dropout
        x = Conv2D(500, conv_filter_size_2, padding='valid', activation='relu', kernel_regularizer=regularizers.l2(0.0005), kernel_initializer='glorot_uniform')(x)
        #model.add(Dense(depth_f1, activation='relu', kernel_regularizer=regularizers.l2(0.0005), kernel_initializer='glorot_normal'))
        x = Dropout(keep_prob)(x)
        x = Conv2D(num_labels, 1, padding='valid', activation='softmax', kernel_regularizer=regularizers.l2(0.0005), kernel_initializer='glorot_uniform')(x)
        
        model = Model(input_img, x)

        if weightsPath is not None:
            model.load_weights(weightsPath)
        
        return model
    
def run_training(dataset,
                 labels,
                 learning_rate,
                 decay_rate,
                 momentum,
                 num_steps,
                 num_labels,
                 keep_prob,
                 save_file,
                 weigths_file,
                 num_gpus,
                 steps_per_epoch=None,
                 weightsPath=None,
                 batch_size=None,
                 train_size=None,
                 target_size=None,
                 validation_data=None): 
    init_time = time.time()
    
    img_shape = (dataset.shape[1], dataset.shape[2], dataset.shape[3])
    
    #run_options = tensorflow.RunOptions(trace_level=tensorflow.RunOptions.FULL_TRACE)
    #run_metadata= tensorflow.RunMetadata()
   
    #Tamanho do resample
    valid_size = min(dataset.shape[0] - train_size, batch_size)
    train_data = dataset[0:train_size]
    train_labels = labels[0:train_size]
    valid_data = dataset[train_size:]
    valid_labels = labels[train_size:]
    
    # Uso do meu callback para pegar o tempo por iteração
    iter_time = CountTime()
    new_model = FCN_Lenet5(num_labels=num_labels, keep_prob=keep_prob, weightsPath=weightsPath, img_shape=img_shape)
    sgd = optimizers.SGD(lr=learning_rate, decay=decay_rate, momentum=momentum, nesterov=False)
    if num_gpus == 1 or num_gpus == 0:
        new_model.compile(optimizer=sgd,
                    loss='binary_crossentropy',
                    metrics=['accuracy'])

        #new_model.compile(optimizer=sgd,
        #            loss='binary_crossentropy',
        #            metrics=['accuracy'],
        #            options=run_options,
        #            run_metadata=run_metadata)
    else:        
        parallel_model = multi_gpu_model(new_model, gpus=num_gpus)
        parallel_model.compile(optimizer=sgd,
                    loss='binary_crossentropy',
                    metrics=['accuracy'])

       # parallel_model.compile(optimizer=sgd,
       #             loss='binary_crossentropy',
       #             metrics=['accuracy'],
       #             options=run_options,
       #		    run_metadata=run_metadata)
    
    new_model.summary()

    if weightsPath is None:
        print("Training ...")
        init_final_time = time.time() - init_time
        print("Tempo de inicializacao:", init_final_time)
        #checkpointer = ModelCheckpoint(weigths_file, monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=False, mode='min', period=1)
        early_stopping = EarlyStopping(monitor='val_acc', min_delta=0.001, patience=5, verbose=0, mode='auto', baseline=0.9000, restore_best_weights=False)
        if num_gpus == 1 or num_gpus == 0:
            history = new_model.fit(train_data, train_labels, epochs=num_steps, batch_size=batch_size, steps_per_epoch=steps_per_epoch, validation_data=validation_data, callbacks=[early_stopping, iter_time])
        else:
            history = parallel_model.fit(train_data, train_labels, epochs=num_steps, batch_size=batch_size, steps_per_epoch=steps_per_epoch, validation_data=validation_data, callbacks=[early_stopping, iter_time])
    
        print("Modelo salvo:" + save_file)
        new_model.save(save_file, overwrite=True)

        #from tensorflow.python.client import timeline
        #tl = timeline.Timeline(run_metadata.step_stats)
        #ctf = tl.generate_chrome_trace_format()
        #with open('output/timeline.json', 'w') as f:
        #    f.write(ctf)

    return history

def esemble(data, image_shape, verbose=True):

    # Recria o grafo para realizar a inferencia
    data = np.reshape(data, (1, data.shape[0], data.shape[1], data.shape[2]))
    matrix_prediction = np.zeros((9,1,126,751,2), dtype=np.float) #9 linhas por n colunas
    final_prediction = np.zeros((1, 126, 751, 2), dtype=np.float)
    img_shape = image_shape
    
    # Realiza Inferencia para todos os modelos treinados
    start_time = time.time()
    for i in range(9):
        weights = 'model_augmentation/' + model_name + '/FCN_' + model_name + '_' + str(i) +'_64x64.hdf5'
       
        # Faz a inferencia
        start_time = time.time()
        model = FCN_Lenet5(2,img_shape=img_shape)
        model.load_weights(weights)
        
        matrix_prediction[i] = model.predict(data)
    
    # Verifica a media na predicao de todos os modelos 
    final_prediction = matrix_prediction.mean(axis=0)   
    duration = time.time() - start_time
    if (verbose): print("Inferencia concluida. Tempo: %.1fs" % duration)

    return final_prediction
