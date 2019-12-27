import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model
import numpy as np
import random, os, sys

from collections import deque


sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "per/")
from per.prioritized_memory import Memory 


class DeepQModel(object):
    """Constructs the desired deep q learning network"""
    def __init__(self, num_actions, num_frames, TAU=100, lr=0.0025, intEpsilon = 0.2):
        
        self.num_actions = num_actions
        self.num_frames = num_frames
        self.TAU = TAU
        self.counter_TAU = 0
        self.lr = lr

        self.EPSILON_DECAY = 100000
        self.FINAL_EPSILON = 0.05
        self.INITIAL_EPSILON = intEpsilon
        self.epsilon = intEpsilon
        self.gamma = 0.99

        self.MEMORY_SIZE = 40000
        self.MINIBATCH_SIZE = 32

        #self.memory = deque(maxlen=self.MEMORY_SIZE)
        self.memory = Memory(self.MEMORY_SIZE)

        self.optimizer = keras.optimizers.Adam(lr = self.lr)
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
        #model.compile(loss='mse', optimizer=Adam(lr=self.lr))

        return model

    def replay(self):

        #minibatch = random.sample(self.memory, self.MINIBATCH_SIZE)
        minibatch, idxs, is_weights = self.memory.sample(self.MINIBATCH_SIZE)
        states = np.array([val[0] for val in minibatch ])
        actions = np.array([val[1] for val in minibatch ])
        rewards = np.array([val[2] for val in minibatch ])
        next_states = np.array([val[3] for val in minibatch ])
        dones = np.array([val[4] for val in minibatch ])


        t = self.target_model.predict(next_states)

        for i in range(len(dones)):
            if dones[i]:
                t[i][actions[i]] = rewards[i]
            else:
                t[i][actions[i]] = rewards[i] + self.gamma*np.max(t[i])


        #loss = self.model.train_on_batch(states, t, sample_weight = is_weight)
        absolute_error = None
        loss_value = None

        with tf.GradientTape() as tape:
            one_hot_actions = tf.one_hot(actions, self.num_actions)
            logits = self.model(states)
            Q_log = tf.math.reduce_sum(tf.math.multiply(one_hot_actions, logits),axis=1)
            Q_t = tf.math.reduce_sum(tf.math.multiply(one_hot_actions, t),axis=1)
            diff = tf.math.subtract(Q_log,Q_t)

            absolute_error = keras.backend.abs(diff)
            

            loss_value = tf.math.reduce_mean(is_weights * tf.math.squared_difference(Q_log, Q_t))
            #loss_value = keras.losses.mse(t,logits)
            grads = tape.gradient(loss_value, self.model.trainable_weights)
            self.optimizer.apply_gradients(zip(grads, self.model.trainable_weights))

        for i, idx in enumerate(idxs):
            self.memory.update(idx,absolute_error[i])



        self.epislon_decay()
        return loss_value
        


    def remember(self, sample):
        error = np.max(self.memory.tree.tree[-self.memory.tree.capacity:])
        if error == 0:
            error = 1
        self.memory.add(error, sample)


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

