from tensorflow.keras.callbacks import Callback
from tensorflow.keras import regularizers
from tensorflow.keras.layers import BatchNormalization, LeakyReLU, Conv2D, add,\
    Flatten, MaxPooling2D, Dense, Reshape, Input, Dropout, concatenate
from tensorflow.keras.models import Model, Sequential
import tensorflow.keras.utils
import numpy as np
import copy

class ModelHandler:


    def createArchitecture(self,model_type,num_classes,input_shape,chain,strategy):
        '''
        Returns a NN model.
        modelType: a string which defines the structure of the model
        numClasses: a scalar which denotes the number of classes to be predicted
        input_shape: a tuple with the dimensions of the input of the model
        chain: a string which indicates if must be returned the complete model
        up to prediction layer, or a segment of the model.
        '''

        if(model_type == 'inception_single'):
            input_inc = Input(shape = input_shape)

            tower_1 = Conv2D(4, (1,1), padding='same', activation='relu')(input_inc)
            tower_1 = Conv2D(8, (2,2), padding='same', activation='relu')(tower_1)
            tower_1 = Conv2D(16, (3,3), padding='same', activation='relu')(tower_1)
            tower_2 = Conv2D(4, (1,1), padding='same', activation='relu')(input_inc)
            tower_2 = Conv2D(16, (3,3), padding='same', activation='relu')(tower_2)
            tower_2 = Conv2D(16, (5,5), padding='same', activation='relu')(tower_2)
            tower_3 = MaxPooling2D((3,3), strides=(1,1), padding='same')(input_inc)
            tower_3 = Conv2D(4, (1,1), padding='same', activation='relu')(tower_3)

            output = concatenate([tower_1, tower_2, tower_3], axis = 3)


            if(chain=='segment'):
                architecture = output

            else:
                output = Dropout(0.25)(output)
                output = Flatten()(output)
                out = Dense(num_classes,activation='softmax')(output)

                architecture = Model(inputs = input_inc, outputs = out)

        elif(model_type == 'light_image'):
            input_inc = Input(shape = input_shape)
	    print("input_shape- img",input_shape)
	    # all the filters are doubled
            #tower_1 = Conv2D(16, (2,2), padding='same', activation='relu', use_bias= True,kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=1e-4),bias_regularizer=regularizers.l2(0.01), activity_regularizer=regularizers.l2(0.01))(input_inc)
            tower_1 = Conv2D(16, (2,2), padding='same', activation='relu')(input_inc)
	    tower_1 = MaxPooling2D((2,2), strides=(1,1), padding='same')(tower_1)
            #tower_1 = Conv2D(20, (3,3), padding='same', activation='relu', use_bias= True,kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=1e-4),bias_regularizer=regularizers.l2(0.01), activity_regularizer=regularizers.l2(0.01))(tower_1)
	    tower_1 = Conv2D(20, (3,3), padding='same', activation='relu')(tower_1)
            tower_1 = MaxPooling2D((2,2), strides=(1,1), padding='same')(tower_1)
            tower_1 = Conv2D(24, (9,9), padding='same', activation='relu')(tower_1)
            #output = concatenate([tower_1, tower_2, tower_3], axis = 3)
            output = tower_1

            #output = Dropout(0.25)(output)
            output = Flatten()(output)
            out = Dense(512,activation='relu')(output) # added
            if strategy == 'one_hot':
                out = Dense(num_classes,activation='softmax')(output)
            elif strategy == 'reg':
                out = Dense(num_classes)(output)

            architecture = Model(inputs = input_inc, outputs = out)


        elif(model_type == 'coord_mlp'):
            #initial 4,16,64
            input_coord = Input(shape = (input_shape,))
	    print("input_shape- coord",input_shape)
            #Model 1
            # layer = Dense(64,activation='relu')(input_coord)
            # layer = Dense(16,activation='relu')(layer)
            # layer = Dense(4,activation='relu')(layer)
            #Model 2
            #layer = Dense(128,activation='relu',use_bias= True,kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=1e-4),bias_regularizer=regularizers.l2(0.01), activity_regularizer=regularizers.l2(0.01))(input_coord)
            #layer = Dense(64,activation='relu', use_bias= True,kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=1e-4),bias_regularizer=regularizers.l2(0.01), activity_regularizer=regularizers.l2(0.01))(layer)
            layer = Dense(128,activation='relu', use_bias = True)(input_coord)
            layer = Dense(64,activation='relu', use_bias= True)(layer)
	    layer = Dense(16,activation='relu')(layer)
            layer = Dense(32,activation='relu')(layer)
            layer = Dense(4,activation='relu')(layer)
            if strategy == 'one_hot':
                out = Dense(num_classes,activation='softmax')(layer)
            elif strategy == 'reg':
                out = Dense(num_classes)(layer)

            architecture = Model(inputs = input_coord, outputs = out)

        elif(model_type == 'lidar_marcus'):
            dropProb=0.3
            print("input_shape- lidar",input_shape)
            input_lid = Input(shape = input_shape)
	    #  NUMBER OF FILTERS ARE DOUBLED
            layer = Conv2D(20,kernel_size=(13,13),
                                activation='relu',
                                padding="SAME",
                                input_shape=input_shape)(input_lid)
            #layer = Conv2D(60, (11, 11), padding="SAME", activation='relu', use_bias= True,kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=1e-4),bias_regularizer=regularizers.l2(0.01), activity_regularizer=regularizers.l2(0.01))(layer)
            #layer = Conv2D(50, (9, 9), padding="SAME", activation='relu', use_bias= True,kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=1e-4),bias_regularizer=regularizers.l2(0.01), activity_regularizer=regularizers.l2(0.01))(layer)
	    layer = Conv2D(60, (11, 11), padding="SAME", activation='relu')(layer)
            layer = Conv2D(50, (9, 9), padding="SAME", activation='relu')(layer)
            layer = MaxPooling2D(pool_size=(2, 1))(layer)
            layer = Dropout(dropProb)(layer)
            layer = Conv2D(40, (7, 7), padding="SAME", activation='relu')(layer)
            layer = MaxPooling2D(pool_size=(1, 2))(layer)
            layer = Conv2D(30, (5, 5), padding="SAME", activation='relu')(layer)
            layer = Dropout(dropProb)(layer)
            layer = Conv2D(20, (3, 3), padding="SAME", activation='relu')(layer)
            #layer = Conv2D(1, (1, 1), padding="SAME", activation='relu')(layer) # commneted out
            layer = Flatten()(layer)
	    #layer = Dense(256,activation='softmax')(layer) # added
            if strategy == 'one_hot':
                out = Dense(num_classes,activation='softmax')(layer)
            elif strategy == 'reg':
                out = Dense(num_classes)(layer)

            architecture = Model(inputs = input_lid, outputs = out)



        return architecture
