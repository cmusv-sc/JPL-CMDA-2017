#== class_PCA
  #== def_PCA_init
    #== get_mask
    #== process_weight
  #== def_demask():
  #== def_demean()
  #== def_timeweight()
  #== def_svd():
  #== def_svd2():
  #== def_addmean()
  #== def_putmask():
  #== def_calculate(self):
  #== def_calculate2(self):

'''
Notes:

- There are 3 steps in data processing, and they should be done in the following order:
 demask, demean, timeweight.

When processing patterns, the order should be:
 divideweight, putmask

# move it to cmac 
kk py
rsyn -av pca_v4.py  /home/btang/projects/cmac/git/JPL-WebService/services/svc/svc/src/py

'''

import numpy as np
import time

#== class_PCA
class PCA:
  #== def_PCA_init
  def __init__(self, \
data, \
mask=None, \
missingvalue=None, \
nkeep=20, \
weight=None \
):

    self.data = data
    self.shape = data.shape

    self.arrayType = data.dtype
    self.nTime = self.shape[0]
    if nkeep is None:
      self.nKeep = min(data.shape)
    else:
      self.nKeep = nkeep

    self.weight = weight

    if self.weight is None:
      self.isWeight = None
    else:
      self.isWeight = True

    #== process_weight
    '''
    self.weight -- the original weight
    self.weight1 -- demasked weight
    self.weight2 -- de-zero, demasked weight
'''

  #== def_timeweight()
  '''
multiply weight
- Use it after demask.
'''
  def timeweight(self):
    if self.isWeight:
      self.data *= self.weight[np.newaxis, :]

  #== def_svd():
  def svd(self):
    print 'start svd calculation. Matrix size=%d x %d, type=%s' \
     %(self.data.shape[0], self.data.shape[1], self.data.dtype)
    #print self.data.shape
    #print type(self.data)
    U,L,V = np.linalg.svd(self.data)

    self.var= L*L
    self.variance= self.var
    self.varP = self.var\
     / np.array( np.sum(self.var) )

    print 'Done. Variance (%%)=%.3f, %.3f, %.3f, %.3f' \
     %(self.varP[0], self.varP[1], \
       self.varP[2], self.varP[3])

    self.nKeep = min(np.size(L), self.nKeep)
    nKeep = self.nKeep

    self.tser = U[:, :nKeep].T
    self.pattern = V[:nKeep, :]

    #print self.tser.shape
    #print L.shape
    self.tser *= L[:nKeep, np.newaxis]

  #== def_svd2():
  def svd2(self):
    nTime = self.data.shape[0]
    nPoint = self.data.shape[1]
    print 'start svd calculation. Matrix size=%d x %d, type=%s' \
     %(nTime, nPoint, self.data.dtype)

    t0 = time.time()
    t0a = time.time()

    if nPoint > nTime:
      a1 = np.dot(self.data, self.data.T)
    else:
      a1 = np.dot(self.data.T, self.data)
    print "make cov dt = %.2f"%(time.time()-t0a)

    t0a = time.time()
    s2, v2 = np.linalg.eigh(a1)
    print "eigh  dt = %.2f"%(time.time()-t0a)

    ds = s2[1:] - s2[:-1]
    if np.any(ds<0):
      print ds
      return

    t0a = time.time()
    s2 = s2[::-1]
    v2 = v2[:, ::-1]

    self.nKeep = min(np.size(s2), self.nKeep)
    nKeep = self.nKeep

    v2 = v2[:, :nKeep]

    print "self.data.shape, v2.shape, s2.shape, nKeep: ",
    print self.data.shape, v2.shape, s2.shape, nKeep
    print "np.sqrt(s2[:nKeep]).shape: ",
    print np.sqrt(s2[:nKeep]).shape
    if nPoint > nTime:
      u2 = np.dot(v2.T, self.data) / np.sqrt(s2[:nKeep])[:, np.newaxis]
      self.tser = v2.T
      self.pattern = u2
    else:
      u2 = np.dot(self.data, v2) / np.sqrt(s2[:nKeep])[np.newaxis, :]
      self.tser = u2.T
      self.pattern = v2.T

    print "make u  dt = %.2f"%(time.time()-t0a)

    #print u.shape, v.shape
    t1 = time.time()
    print "data of %d x %d.  dt = %.2f"%(nTime, nPoint, t1-t0)

    self.var= s2
    self.variance= self.var
    self.varP = self.var\
     / np.array( np.sum(self.var) )

    print 'Done. Variance (%%)=%.3f, %.3f, %.3f, %.3f' \
     %(self.varP[0], self.varP[1], \
       self.varP[2], self.varP[3])

    self.tser *= np.sqrt(s2[:nKeep])[:, np.newaxis]

    # flip sign to make the largest magnitude to be positive
    for iKeep in range(nKeep):
      max1 = self.tser[iKeep].max()
      min1 = self.tser[iKeep].min()
      if max1<0 or (max1*min1<0 and max1<-min1):
        self.tser[iKeep] *= -1.0
        self.pattern[iKeep] *= -1.0

  #== def_divideweight():
  def divideweight(self):
    if self.isWeight:
      self.data /= self.weight[np.newaxis, :]
      self.pattern /= self.weight[np.newaxis, :]

  #== def_calculate(self):
  def calculate(self):
    #self.demask()
    #self.demean()
    self.timeweight()
    self.svd()
    #self.putmask()
    self.divideweight()
    #self.addmean()
      
  #== def_calculate2(self):
  def calculate2(self):
    #self.demask()
    #self.demean()
    self.timeweight()
    self.svd2()
    #self.putmask()
    self.divideweight()
    #self.addmean()
 
