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
        self.last_score = 0

    def calculateReward(self, score, done):
        if score > self.max:
            self.max = score
        """
        if self.last_score < score:
            self.last_score = score
            return 1 
        if self.last_score > score:
            self.last_score = score
            return -1 # Scored lowered, something bad happend
        
        if done:
            if self.last_score >= self.MAX_SCORE:
                return 2 # we reached our goal :D
            return -2 # We failed to achieve the end MAX_SCORE
	"""
        if done:
            temp = (score - self.MAX_SCORE)#/self.MAX_SCORE + 1
            temp = temp*2
            if temp > 0:
                return min(50, temp)
            else:
                return -2
        
        temp =  abs(self.last_score - score) #* (1- self.last_score/score)
        self.last_score = score
        if temp > 0:
            return min(20, temp)
        elif temp < 0:
            return max(-20, temp) 
        else:
            return -2 # We didn't improve

    def calculateTotalReward(self):
        return self.max

    def reset(self, init_score):
        self.max = 0
        self.last_score = init_score



class CombinedRewards(AbstractRewards):


    def __init__(self, MAX_FRAMES, MAX_SCORE, p = 0.7, scale = 2):
        super().__init__(MAX_FRAMES, MAX_SCORE)
        self.count_calls = 0
        self.p = p
        self.scale = scale


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
        
        reward = (1-self.p)*(self.count_calls/self.MAX_FRAMES) + self.p*(np.abs(score - self.last_score) -1)*self.scale
        self.last_score = score
        return reward

    def reset(self, score):
        self.last_score = score
        self.count_calls = 0

    def calculateTotalReward(self):
        return (1-self.p)*(self.count_calls/self.MAX_FRAMES) + self.p*self.last_score
        
