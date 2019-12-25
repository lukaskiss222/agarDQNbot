import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import load_model

class DeepQModel(object):
    """Constructs the desired deep q learning network"""
    def __init__(self, num_actions, num_frames, TAU=10, lr=0.0001):
        self.construct_q_network()
        self.num_actions = num_actions
        self.num_frames = num_frames
        self.TAU = TAU
        self.counter_TAU = 1
        self.lr = lr


        self.model = self.construct_q_network()
        self.target_model = self.construct_q_network()
        self.target_model.set_weights(self.model.get_weights())


    def construct_q_network(self):

        # Uses the network architecture found in DeepMind paper
        model = Sequential()
        model.add(layers.Convolution2D(32, 8, 8, subsample=(4, 4), input_shape=(84, 84, self.num_frames)))
        model.add(layers.Activation('relu'))
        model.add(layers.Convolution2D(64, 4, 4, subsample=(2, 2)))
        model.add(layers.Activation('relu'))
        model.add(layers.Convolution2D(64, 3, 3))
        model.add(layers.Activation('relu'))
        model.add(layers.Flatten())
        model.add(layers.Dense(512))
        model.add(layers.Activation('relu'))
        model.add(layers.Dense(self.num_actions))
        model.compile(loss='mse', optimizer=Adam(lr=self.lr))

        return model



    def save_network(self, path):
        # Saves model at specified path as h5 file
        self.model.save(path)
        print("Successfully saved network.")

    def load_network(self, path):
            self.model = load_model(path)
            print("Succesfully loaded network.")

    def target_train(self):
            self.counter_TAU+=1
            if self.counter_TAU % self.TAU  != 0:
                return
            #Change after TAU steps (This one is better)
            self.target_model.set_weights(self.model.get_weights())
            #Continues change
            """
            model_weights = self.model.get_weights()
            target_model_weights = self.target_model.get_weights()
            for i in range(len(model_weights)):
                target_model_weights[i] = TAU * model_weights[i] + (1 - TAU) * target_model_weights[i]
            self.target_model.set_weights(target_model_weights)
            """

