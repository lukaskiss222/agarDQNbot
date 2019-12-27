#Rewards objects
import numpy as np

class AbstractRewards(object):


    def __init__(self, MAX_FRAMES, MAX_SCORE):
        self.MAX_FRAMES = MAX_FRAMES
        self.MAX_SCORE = MAX_SCORE


    def calculateReward(self, score, done):
        raise NotImplementedError()

    def calculateTotalReward(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

class SimpleRewards(AbstractRewards):

    def __init__(self, MAX_FRAMES, MAX_SCORE):
        super().__init__(MAX_FRAMES, MAX_SCORE)
        self.max = 0

    def calculateReward(self, score, done):
        if done:
            return -1
        if score > self.max:
            self.max = score
        return score

    def calculateTotalReward(self):
        return self.max

    def reset(self):
        self.max = 0



class CombinedRewards(AbstractRewards):


    def __init__(self, MAX_FRAMES, MAX_SCORE, initial_score, p = 0.7):
        super().__init__(MAX_FRAMES, MAX_SCORE)
        self.initial_score = initial_score
        self.last_score = initial_score
        self.count_calls = 0
        self.p = p


    def calculateReward(self, score, done):
        """
        Punishing for not eating and dying
        Rewarded for gaining higher score
        """
        self.count_calls+=1
        if done:
            if score >= self.MAX_SCORE:
                return 100
            if self.count_calls >= self.MAX_FRAMES:
                return 100
            return -10
        
        reward = (1-p)*(self.count_calls/self.MAX_FRAMES) + p*(np.abs(score - self.last_score) -1)
        self.last_score = score
        return reward

    def reset(self):
        self.last_score = self.initial_score
        self.count_calls = 0

    def calculateTotalReward(self):
        return (1-p)*(self.count_calls/self.MAX_FRAMES) + p*self.last_score
        