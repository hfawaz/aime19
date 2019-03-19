import numpy as np
import operator
from dba import dba
from distances.dtw.dtw import  dynamic_time_warping as dtw

def kmeans(tseries, nbclusters, nb_iterations = 10, init_clusters = None,
           averaging_algorithm = 'dba', distance_algorithm = 'dtw'):
    """
    Performs the k-means algorithm using the averaging algorithm specified. 
    :param tseries: The list of time series on which we would like to apply k-means. 
    :param nb_iterations: Maximum number of k-means iterations. 
    :param nbclusters: The number of clusters a.k.a 'k' in the k-means  
    """
    # get the averaging method (check constants.py)
    avg_method = dba
    # get the distance method (check constants.py)
    distance_method = dtw
    # get dsitance method parameters 
    distance_method_params = {'w':-1}

    # init the clusters 
    if init_clusters is None: 
        # init the k-means algorithm randomly 
        clusterIdx = np.random.permutation(len(tseries))[:nbclusters]
        clusters = [tseries[i] for i in clusterIdx]
    else: 
        clusters = init_clusters
    
    for i in range(nb_iterations):
        # affect the time series to its closest clusters 
        affect = []
        # init array of distance to closest cluster for each time series 
        distances_clust = []
        # start the affectation of each time series 
        for idx_series , series in enumerate(tseries):
            # initialize the cluster index of the series 
            cidx = -1
            # initialize the minimum distance to a cluster 
            minDist = np.inf
            # loop through all clusters 
            for i, cluster in enumerate(clusters):
                # calculate the distance between the cluster and the series 
                dist, __ = distance_method(series, cluster, **distance_method_params)
                # check if it is better than best so far minimum distance 
                if dist < minDist:
                    # assign the new cluster and the minimum distance 
                    minDist = dist
                    cidx = i
            # add the best cluster index to the affectation array 
            affect.append(cidx)
            # this is used to solve the empty clusters problem 
            distances_clust.append((idx_series,minDist))
            
        # empty clusters list 
        empty_clusters=[]
        # recompute the clusters 
        for i in range(nbclusters):
            # get the new group of time series affected to cluster index i 
            current = [tseries[j] for j, x in enumerate(affect) if x == i] 
            # check if cluster is empty 
            if len(current)==0: 
                # add the cluster index to the empty clusters list
                empty_clusters.append(i)
                print('Empty cluster')
                # skip averaging an empty cluster
                continue 
            # compute the new avg or center of this cluster
            dba_avg = avg_method(np.array(current))
            # assign this new cluster center whose index is i
            clusters[i] = dba_avg
            
        # check if we have empty clusters  
        if len(empty_clusters)>0: 
            # sort the distances to get the ones furthest from their clusters 
            distances_clust.sort(key=operator.itemgetter(1),reverse=True)
            # loop through the empty clusters 
            for i,idx_clust in enumerate(empty_clusters): 
                # replace the empty cluster with the farest time series from its old cluster 
                clusters[idx_clust] = tseries[distances_clust[i][0]]
    
    # re-affectation 
    # affect the time series to its closest clusters 
    affect = []
    # start the affectation of each time series 
    for series in tseries:
        # initialize the cluster index of the series 
        cidx = -1
        # initialize the minimum distance to a cluster 
        minDist = np.inf
        # loop through all clusters 
        for i, cluster in enumerate(clusters):
            # calculate the distance between the cluster and the series 
            dist, __ = distance_method(series, cluster,**distance_method_params)
            # check if it is better than best so far minimum distance 
            if dist < minDist:
                # assign the new cluster and the minimum distance 
                minDist = dist
                cidx = i
        # add the best cluster index to the affectation array 
        affect.append(cidx)
    
    # return the clusters as well as the corre
    return clusters, affect