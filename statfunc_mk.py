
def regr(x,y,TLS_flag=0,add_int=0):
	
	#computes the regression coefficients for y = xB
	#if add_int flag is 1, then a column of 1s is included in x to fit an
	#   intercept
	#the TLS flag indicates whether total least squares should be used; if 0,
	#   then OLS
	#if more than one dimension, x and y should be column data; any centering
	#   should be done before input

	import numpy as np
	from scipy import linalg
	
	if np.size(np.shape(x))==1:
		x = x[:,None]
	if np.size(np.shape(y))==1:
		y = y[:,None]
	
	n,m = np.shape(x)
	
	if np.shape(y)[0] != n: 
		raise ValueError('x and y must have matching first dimension')
	
	if add_int==1:
		x = np.hstack((np.ones((n,1)),x))
		
	if TLS_flag==1:
		z = np.hstack((x,y))
		u,s,v1 = linalg.svd(z)
		beta = np.dot(linalg.inv(np.dot(x.T,x)-(s[m]**2)*np.identity(m)),np.dot(x.T,y))
	else:
		beta = np.dot(linalg.inv(np.dot(x.T,x)),np.dot(x.T,y))

	return beta
	
###############################################################################
def AIC(x,y,add_int=0):
	
	#calculates the Akaike Information Criterion (AIC) for predictor selection
	# in a regression analysis
	# 
	# Equations from Seber and Lee (2003) and output checked against the R function
	
	import numpy as np
	from scipy import linalg
	
	if np.size(np.shape(x))==1:
		x = x[:,None]
	if np.size(np.shape(y))==1:
		y = y[:,None]
	
	n,p = np.shape(x)
	
	if np.shape(y)[0] != n: 
		raise ValueError('x and y must have matching first dimension')
	
	if add_int==1:
		x = np.hstack((np.ones((n,1)),x))
		
	beta = np.dot(linalg.inv(np.dot(x.T,x)),np.dot(x.T,y))	

	rss = np.dot(y.T,y) - np.dot(beta.T,np.dot(x.T,np.dot(x,beta)))
	aic = n*np.log(2*np.pi*rss/n)+n+2*(p+1)

	return aic

###############################################################################
def AIC_cv(y,yhat,p):
	
	# similar to AIC function above but designed for cross-validataion
	# inputs are the dependent variable y and the residual yhat; p is the
	#   number of parameters of the regression model 
	
	import numpy as np
	
	if np.shape(y)!=np.shape(yhat):
		raise ValueError('y and yhat must be the same size')
	if len(y)!=len(y.flatten()):
		raise ValueError('only vector input is accepted')

	n = len(yhat[~np.isnan(yhat)])

	rss = np.nansum((y-yhat)**2)
	aic = n*np.log(2*np.pi*rss/n)+n+2*(p+1)

	return aic
	
###############################################################################

def CItoEB(CI,x):
	
	#input an nx2 array of CI bounds and their corresponding variable in the 
	#   nx1 array x
	#output is a nx2 array of error bar values (to be used in plotting)
	
	import numpy as np
	
	n = np.shape(CI)
	nx = np.shape(x)
	
	if np.size(nx)>2:
		raise ValueError('x cannot have more than 2 dimensions')
	elif np.size(nx)>1 and 1 not in nx:
		raise ValueError('x must be a vector')
		
	
	if 2 not in n:
		raise ValueError('one dimension of CI must be of size 2')
	elif np.size(n)>2:
		raise ValueError('variable CI cannot have more than 2 dimensions')
	if np.size(n)==1:
		CI = CI[None,:]
		n = np.hstack((1,n))
	elif n[1]!=2:
		CI = CI.T
		
	if np.size(x) != np.shape(CI)[0]:
		raise ValueError('CI and x must have a common dimension')
	
	
	x = np.squeeze(x)
	eb = np.zeros(n)	
	
	eb[:,0] = x-CI[:,0]
	eb[:,1] = CI[:,1]-x
	
	return eb

###############################################################################


def autocorr(x, lags='None'):
	
	#returns the autocorrelation of x at lags
	#should input x with mean/seasonal cycle removed
	#adapted from Dan's matlab function
	
	import numpy as np
	
	if lags is 'None':
		lags = np.arange(11) #default to lags 0-10
		
		
	#make sure x and lags are both numpy arrays
	x = np.array(x)
	lags = np.atleast_1d(lags)
	
	n = np.shape(x)
	if np.size(n) > 2:
		raise ValueError('input has too many dimensions')
	elif np.size(n)==2 and n[0]>1 and n[1]>1:
		raise ValueError('Please input a vector')
	

	nlag = np.size(lags)
	nt = np.size(x)
	ac = np.zeros((nlag,))
	
	for i in np.arange(nlag):
		x1 = x[:(nt-np.abs(lags[i]))]
		x2 = x[np.abs(lags[i]):]
		z = np.corrcoef(x1,x2)
		ac[i] = z[0,1]
	
	return ac

################################################################################
def std_weighted(x,weights):
	
	import numpy as np
	
	n1 = np.size(weights[weights>0])
	
	mn_w = np.sum(x*weights)/np.sum(weights)
	
	num = np.sum(weights*(x-mn_w)**2)
	den = (n1-1)*np.sum(weights)/n1
	
	stw = np.sqrt(num/den)
	
	return stw
	
################################################################################
def stderr_weighted(x, weights):
	
	#computes the standard error for a weighted mean following Cochran (1977)
	#  which was found to be the closest estimate to bootstrapping by Gatz
	#  and Smith (1995)
	# see http://stats.stackexchange.com/questions/25895/computing-standard-error-in-weighted-mean-estimation
	
	import numpy as np
	
	n = np.size(weights)
	if np.size(x)!=n:
		raise ValueError('size of weights must match size of input data')
	
	mxw = np.sum(x*weights)/np.sum(weights)	#weighted mean
	mx = np.mean(weights)		#mean of weights
	
	se1 = n/((n-1)*np.sum(weights)**2)*(np.sum((weights*x-mx*mxw)**2)
			-2*mxw*np.sum((weights-mx)*(weights*x-mx*mxw))+mxw**2*np.sum((weights-mx)**2))
	
	se = np.sqrt(se1)
  
	return se

###############################################################################
def det_percentile(x1,x):
	
	# determines the percentile of the value(s) in x1 in the set of data in x
	
	import numpy as np
	from scipy import stats
	
	n = np.size(x1)

	if n==1:
		y = np.hstack((x.flatten(),x1))
		r = stats.mstats.rankdata(np.ma.masked_invalid(y))
		p = (100./len(r[r>0])) * (r[-1] - 0.5)		
	else:
		p = np.zeros((n))	
		
		for i in xrange(n):
			y = np.hstack((x.flatten(),x1[i]))
			r = stats.mstats.rankdata(np.ma.masked_invalid(y))
			p[i] = (100./len(r[r>0])) * (r[-1] - 0.5)
	
	return p

###############################################################################











	
	