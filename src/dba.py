import numpy as np
from distances.dtw.dtw import  dynamic_time_warping as dtw

def calculate_dist_matrix(tseries, dist_fun, dist_fun_params):
    N = len(tseries)
    pairwise_dist_matrix = np.zeros((N,N), dtype = np.float64)
    # pre-compute the pairwise distance
    for i in range(N-1):
        x = tseries[i]
        for j in range(i+1,N):
            y = tseries[j] 
            dist = dist_fun(x,y,**dist_fun_params)[0] 
            # because dtw returns the sqrt
            dist = dist*dist 
            pairwise_dist_matrix[i,j] = dist 
            # dtw is symmetric 
            pairwise_dist_matrix[j,i] = dist 
        pairwise_dist_matrix[i,i] = 0 
    return pairwise_dist_matrix

def medoid(tseries, dist_fun, dist_fun_params):
    """
    Calculates the medoid of the given list of MTS
    :param tseries: The list of time series 
    """
    N = len(tseries)
    if N == 1 : 
        return 0,tseries[0]
    pairwise_dist_matrix = calculate_dist_matrix(tseries, dist_fun, 
                                                 dist_fun_params)
        
    sum_dist = np.sum(pairwise_dist_matrix, axis = 0)
    min_idx = np.argmin(sum_dist)
    med = tseries[min_idx]
    return min_idx, med

def _dba_iteration(tseries, avg, dist_fun, dist_fun_params,weights):
    """
    Perform one weighted dba iteration and return the new average 
    """
    # the number of time series in the set
    n = len(tseries)
    # length of the time series 
    ntime = avg.shape[0]
    # number of dimensions (useful for MTS)
    num_dim = avg.shape[1]
    # array containing the new weighted average sequence 
    new_avg = np.zeros((ntime,num_dim),dtype=np.float64)
    # array of sum of weights 
    sum_weights = np.zeros((ntime,num_dim),dtype=np.float64)
    # loop the time series 
    for s in range(n): 
        series = tseries[s]
        dtw_dist, dtw = dist_fun(avg, series, **dist_fun_params)
        
        i = dtw.shape[0]-1
        j = dtw.shape[1]-1

        permute = False
        if ntime + 1 == dtw.shape[1]:
            permute = True

        while i >= 1 and j >= 1:

            if permute == True:
                new_avg[j - 1] += series[i - 1] * weights[s]
                sum_weights[j - 1] += weights[s]
            else:
                new_avg[i - 1] += series[j - 1] * weights[s]
                sum_weights[i - 1] += weights[s]

            a = dtw[i - 1, j - 1]
            b = dtw[i, j - 1]
            c = dtw[i - 1, j]
            if a < b:
                if a < c:
                    # a is the minimum
                    i -= 1
                    j -= 1
                else:
                    # c is the minimum
                    i -=1 
            else:
                if b < c:
                    # b is the minimum
                    j -= 1
                else:
                    # c is the minimum
                    i -= 1
    # update the new weighted avgerage 
    new_avg = new_avg/sum_weights
    
    return new_avg
        
def dba(tseries, max_iter =10, verbose=False, init_avg_method = 'max',
        init_avg_series = None, distance_algorithm = 'dtw', weights=None): 
    """
    Computes the Dynamic Time Warping (DTW) Barycenter Averaging (DBA) of a 
    group of Multivariate Time Series (MTS). 
    :param tseries: A list containing the series to be averaged, where each 
        MTS has a shape (l,m) where l is the length of the time series and 
        m is the number of dimensions of the MTS - in the case of univariate 
        time series m should be equal to one
    :param max_iter: The maximum number of iterations for the DBA algorithm.
    :param verbose: If true, then provide helpful output.
    :param init_avg_method: Either: 
        'random' the average will be initialized by a random time series, 
        'medoid'(default) the average will be initialized by the medoid of tseries, 
        'manual' the value in init_avg_series will be used to initialize the average
    :param init_avg_series: this will be taken as average initialization if 
        init_avg_method is set to 'manual'
    :param distance_algorithm: Determine which distance to use when aligning 
        the time series
    :param weights: An array containing the weights to calculate a weighted dba
        (NB: for MTS each dimension should have its own set of weights)
        expected shape is (n,m) where n is the number of time series in tseries 
        and m is the number of dimensions
    """
    # get the distance function 
    dist_fun = dtw
    # get the distance function params 
    dist_fun_params = {'w':-1}
    # check if given dataset is empty 
    if len(tseries)==0: 
        # then return a random time series because the average cannot be computed 
        start_idx = np.random.randint(0,len(tseries))
        return np.copy(tseries[start_idx])
    
    # init DBA
    if init_avg_method == 'medoid':
        avg = np.copy(medoid(tseries,dist_fun, dist_fun_params)[1])
    elif init_avg_method == 'random': 
        start_idx = np.random.randint(0,len(tseries))
        avg = np.copy(tseries[start_idx])
    elif init_avg_method == 'max': # we initialize with the longest time series
        len_o = -1
        for ts in tseries:
            if len_o < len(ts):
                avg = np.copy(ts)
                len_o = len(ts)
    elif init_avg_method == 'min': # we initialize with the longest time series
        len_o = np.inf
        for ts in tseries:
            if len_o > len(ts):
                avg = np.copy(ts)
                len_o = len(ts)
    else: # init with the given init_avg_series
        avg = np.copy(init_avg_series)
        
    if len(tseries) == 1:
        return avg
    if verbose == True: 
        print('Doing iteration')
        
    # main DBA loop 
    for i in range(max_iter):
        if verbose == True:
            print(' ',i,'...')
        if weights is None:
            # when giving all time series a weight equal to one we have the 
            # non - weighted version of DBA 
            weights = np.ones((len(tseries), tseries[0].shape[1]), dtype=np.float64)
        # dba iteration 
        avg = _dba_iteration(tseries,avg,dist_fun, dist_fun_params,weights)
    
    return avg 
    