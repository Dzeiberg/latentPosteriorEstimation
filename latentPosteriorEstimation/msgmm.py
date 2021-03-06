# AUTOGENERATED! DO NOT EDIT! File to edit: MSGMM.ipynb (unless otherwise specified).

__all__ = ['MSGMM']

# Cell
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import scipy.stats as ss
from tqdm.notebook import tqdm, trange

# Cell
class MSGMM:
    def __init__(self):
        pass
    def updateAlpha(self):
        self.alpha = np.mean(self.wiU)

    def updateBeta(self):
        self.beta = np.mean(self.wiL)

    def updateU1(self, xUnlabeled, xPos):
        self.u1 = (self.wiU.T @ xUnlabeled +self.wiL.T@xPos) / (np.sum(self.wiU) + np.sum(self.wiL))

    def updateU0(self, xUnlabeled, xPos):
        self.u0 = (((1-self.wiU).T@xUnlabeled) + ((1-self.wiL).T@xPos)) / (np.sum(1-self.wiU) + np.sum(1-self.wiL))

    def updateSigma1(self, xUnlabeled, xPos):
        s11 = xUnlabeled - np.repeat(self.u1[None], xUnlabeled.shape[0],0)
        s1 = s11.T @ np.diag(self.wiU.ravel()) @ s11
        s22 = xPos - np.repeat(self.u1[None],xPos.shape[0],0)
        s2 = s22.T @ np.diag(self.wiL.ravel()) @ s22
        self.sigma1 = (s1 + s2) / (np.sum(self.wiU) + np.sum(self.wiL))
    def updateSigma0(self, xUnlabeled, xPos):
        s11= xUnlabeled - np.repeat(self.u0[None],xUnlabeled.shape[0],0)
        s22 = xPos - np.repeat(self.u0[None], xPos.shape[0],0)
        s1 = s11.T @ np.diag(1 - self.wiU.ravel()) @ s11
        s2 = s22.T @ np.diag(1 - self.wiL.ravel()) @ s22
        self.sigma0 = (s1 + s2) / (np.sum(1 - self.wiU) + np.sum(1-self.wiL))

    def fit(self, xUnlabeled, xPos,verbose=True,iterations=100):
        self.wiL = np.random.beta(5,2,size=(xPos.shape[0]))
        self.wiU = np.random.beta(2,5,size=(xUnlabeled.shape[0]))
        for iteration in trange(iterations):
            # M-Step
            self.updateAlpha()
            self.updateBeta()
            self.updateU1(xUnlabeled,xPos)
            self.updateU0(xUnlabeled, xPos)
            self.updateSigma1(xUnlabeled,xPos)
            self.updateSigma0(xUnlabeled,xPos)
            # E-Step
            # Update unlabeled responsibilities
            phi1U= ss.multivariate_normal.pdf(xUnlabeled,mean=self.u1.ravel(),cov=self.sigma1)
            phi0U= ss.multivariate_normal.pdf(xUnlabeled,mean=self.u0.ravel(),cov=self.sigma0)
            self.wiU = self.alpha * phi1U / (self.alpha * phi1U + (1-self.alpha) * phi0U)
            # Update positive responsibilities
            phi1L= ss.multivariate_normal.pdf(xPos,mean=self.u1.ravel(),cov=self.sigma1)
            phi0L= ss.multivariate_normal.pdf(xPos,mean=self.u0.ravel(),cov=self.sigma0)
            self.wiL = self.beta * phi1L / (self.beta * phi1L + (1-self.beta) * phi0L)
            if verbose and not iteration % 5:
                print(np.concatenate((self.sigma1,self.sigma0),axis=1))
                print()
                print(self.alpha, self.beta, self.u1, self.u0)
                print()

    def predict_proba(self,x):
        phi1 = ss.multivariate_normal.pdf(x, mean=self.u1.ravel(),cov=self.sigma1)
        phi0 = ss.multivariate_normal.pdf(x,mean=self.u0.ravel(), cov=self.sigma0)
        return self.alpha * phi1 / (self.alpha * phi1 + (1 - self.alpha) * phi0)