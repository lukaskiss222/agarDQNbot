import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model
from collections import deque
import numpy as np
import random

class DeepQModel(object):
    """Constructs the desired deep q learning network"""
    def __init__(self, num_actions, num_frames, TAU=10, lr=0.0001,):
        
        self.num_actions = num_actions
        self.num_frames = num_frames
        self.TAU = TAU
        self.counter_TAU = 0
        self.lr = lr

        self.EPSILON_DECAY = 1000000
        self.FINAL_EPSILON = 0.05
        self.INITIAL_EPSILON = 0.1
        self.epsilon = 0.1
        self.gamma = 0.99

        self.MEMORY_SIZE = 40000
        self.MINIBATCH_SIZE = 32

        self.memory = deque(maxlen=self.MEMORY_SIZE)


        self.model = self.construct_q_network()
        self.target_model = self.construct_q_network()
        self.target_train()


    def construct_q_network(self):

        # Uses the network architecture found in DeepMind paper
        model = Sequential()
        model.add(layers.Convolution2D(32, (8, 8), strides=(4, 4), input_shape=(84, 84, self.num_frames)))
        model.add(layers.Activation('relu'))
        model.add(layers.Convolution2D(64, (4, 4), strides=(2, 2)))
        model.add(layers.Activation('relu'))
        model.add(layers.Convolution2D(64, (3, 3)))
        model.add(layers.Activation('relu'))
        model.add(layers.Flatten())
        model.add(layers.Dense(512))
        model.add(layers.Activation('relu'))
        model.add(layers.Dense(self.num_actions))
        model.compile(loss='mse', optimizer=Adam(lr=self.lr))

        return model

    def replay(self):

        minibatch = random.sample(self.memory, self.MINIBATCH_SIZE)
        states = np.array([val[0] for val in minibatch ])
        actions = np.array([val[1] for val in minibatch ])
        rewards = np.array([val[2] for val in minibatch ])
        next_states = np.array([val[3] for val in minibatch ])
        dones = np.array([val[4] for val in minibatch ])


        t = self.target_model.predict(next_states)

        for i in range(len(dones)):
            if dones[i]:
                t[actions[i]] = rewards[i]
            else:
                t[actions[i]] = rewards[i] + self.gamma*np.max(t[i])


        loss = self.model.train_on_bacth(states, t)
        self.epislon_decay()
        


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def epislon_decay(self):
        if self.epsilon > self.FINAL_EPSILON:
                self.epsilon -= (self.INITIAL_EPSILON-self.FINAL_EPSILON)/self.EPSILON_DECAY

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.num_actions)
        act_values = self.model.predict(np.expand_dims(state, axis=0))
        return np.argmax(act_values[0]) 


    def save_network(self, path):
        # Saves model at specified path as h5 file
        self.model.save(path)
        print("Successfully saved network.")

    def load_network(self, path):
            self.model = load_model(path)
            print("Succesfully loaded network.")

    def target_train(self):
            if self.counter_TAU % self.TAU  != 0:
                return
            self.counter_TAU+=1
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

