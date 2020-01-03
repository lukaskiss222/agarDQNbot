import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential, Model
from tensorflow.keras import layers, backend, utils
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model
import numpy as np
import random, os, sys

from collections import deque


sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "per/")
from per.prioritized_memory import Memory 


class DeepQModel(object):
    """Constructs the desired deep q learning network"""
    def __init__(self, num_actions, num_frames, TAU=100, lr=0.0025, intEpsilon = 0.2, epislon_decay = 1000):
        
        self.num_actions = num_actions
        self.num_frames = num_frames
        self.TAU = TAU
        self.counter_TAU = 0
        self.lr = lr

        self.EPSILON_DECAY = epislon_decay
        self.FINAL_EPSILON = 0.05
        self.INITIAL_EPSILON = intEpsilon
        self.epsilon = intEpsilon
        self.gamma = 0.99

        self.MEMORY_SIZE = 100000
        self.MINIBATCH_SIZE = 64

        #self.memory = deque(maxlen=self.MEMORY_SIZE)
        self.memory = Memory(self.MEMORY_SIZE)

        self.optimizer = keras.optimizers.Adam(lr = self.lr)
        self.model = self.construct_q_network()
        self.target_model = self.construct_q_network()
        self.target_train()


    def construct_q_network(self):

        # Uses the network architecture found in DeepMind paper
        """
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
        """
        input_states = layers.Input(shape=(120,120,self.num_frames))
        x = layers.Convolution2D(32, (8, 8), strides=(4, 4), input_shape=(84, 84, self.num_frames))(input_states)
        x = layers.Activation('elu')(x)
        x = layers.Convolution2D(64, (4, 4), strides=(2, 2))(x)
        x = layers.Activation('elu')(x)
        x = layers.Convolution2D(64, (3, 3))(x)
        x = layers.Activation('elu')(x)
        x = layers.Flatten()(x)

        h_value = layers.Dense(100, activation='elu', name="h_values")(x)
        value = layers.Dense(1, activation="linear", name="value")(h_value)

        h_raw_adventage = layers.Dense(100, activation="elu")(x)
        raw_adventage = layers.Dense(self.num_actions, activation="linear")(h_raw_adventage)

        #adventage = raw_adventage - K.max(raw_adventage, axes=1, keepdims=True)
        adventage = raw_adventage - layers.Lambda(lambda x: backend.mean(x, axis=1, keepdims=True))(raw_adventage)

        Q_values = value + adventage

        model = Model(inputs=[input_states], outputs=[Q_values])

        #utils.plot_model(model, show_shapes=True)
        return model

    def replay(self):

        #minibatch = random.sample(self.memory, self.MINIBATCH_SIZE)
        minibatch, idxs, is_weights = self.memory.sample(self.MINIBATCH_SIZE)
        is_weights =  is_weights.astype(np.float32)
        states = np.array([val[0] for val in minibatch ])
        actions = np.array([val[1] for val in minibatch ])
        rewards = np.array([val[2] for val in minibatch ], dtype=np.float32)
        next_states = np.array([val[3] for val in minibatch ])
        dones = np.array([val[4] for val in minibatch ])

        """
        next_Q_values = self.target_model.predict(next_states)


        target_Q_values = rewards + (1-dones)*self.gamma*np.max(next_Q_values, axis=1)
        target_Q_values = target_Q_values.astype(np.float32)
        """

        #Double DQN
        next_Q_values = self.model.predict(next_states)
        best_next_actions = np.argmax(next_Q_values, axis=1)
        next_mask = tf.one_hot(best_next_actions, self.num_actions).numpy()
        next_best_Q_values = (self.target_model.predict(next_states)* next_mask).sum(axis=1)

        target_Q_values = rewards + (1-dones)*self.gamma*next_best_Q_values
        target_Q_values = target_Q_values.astype(np.float32)


        loss_value, absolute_error = self._train(states,actions, target_Q_values, is_weights)

        for i, idx in enumerate(idxs):
            self.memory.update(idx,absolute_error[i])



        self.epislon_decay()
        return loss_value 

    @tf.function
    def _train(self, states, actions, target_Q_values, is_weights):
        absolute_error = None
        loss_value = None

        with tf.GradientTape() as tape:
            mask = tf.one_hot(actions, self.num_actions)
            all_Q_values = self.model(states)
            Q_values = tf.math.reduce_sum(all_Q_values * mask ,axis=1)

            diff = tf.math.subtract(Q_values, target_Q_values)
            absolute_error = keras.backend.abs(diff)
            

            loss_value = tf.reduce_mean(is_weights *  tf.square(diff))

            grads = tape.gradient(loss_value, self.model.trainable_weights)
            self.optimizer.apply_gradients(zip(grads, self.model.trainable_weights))

        return loss_value, absolute_error


        


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
            self.counter_TAU = 0
            self.target_model()
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

if __name__ == "__main__":
    d = DeepQModel(9,3)

    for i in range(d.MINIBATCH_SIZE + 2):
        sample = np.zeros((84,84,3), dtype=np.float32), 0, 1.0, np.random.rand(84,84,3), False
        d.remember(sample)
    d.replay()
