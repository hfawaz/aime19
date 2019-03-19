# test nlts 
import numpy as np
from dba import medoid
from dba import dba
from distances.dtw.dtw import  dynamic_time_warping as dtw

import matplotlib.pyplot as plt

def un_fold_set(x_train,averaging_algorithm = 'dba', 
		   distance_algorithm='dtw'):
	"""
	This function takes a set of multivariate time series and up scales them
	using the NLTS method.
	:param x_train: The set of time series to be scaled up
	"""
	# get the averaging method (check constants.py)
	avg_method = dba
	# get the distance function
	dist_fun = dtw
	# get the distance function params
	dist_fun_params = {'w':-1}
	# get the average MTS
	avg_mts = avg_method(x_train, distance_algorithm=distance_algorithm,
						 init_avg_method='max')
	# get the number of training series
	n = len(x_train)
	# get the length of the average mts
	m = avg_mts.shape[0]
	# get the associated elements of each mts in x_train with each element of the average
	elements = compute_associations_by_sequence(avg_mts,x_train, dist_fun, dist_fun_params)
	# get the max number of elements associated to every element of the average sequence
	max_element_nb = np.zeros((m,),dtype=np.int64)
	for e in range(m):
		max_element_nb[e] = len(elements[e][0])
		for s in range(1,n):
			max_element_nb[e] = max(max_element_nb[e], len(elements[e][s]))
	# knowledge inside
	# apply the uniform scaling
	new_x_train = []
	# loop through each mts in x_train
	# this code is converted from
	# https://github.com/fpetitjean/sp2m/blob/master/src/items/SymbolicSequences.java#L256
	for s in range(n):
		new_mts = []
		for e in range(m):
			required_nb_elements = max_element_nb[e]
			actual_nb_elements = len(elements[e][s])
			for r in range(required_nb_elements):
				if required_nb_elements==1 :
					pos_in_curr_group = 1.0
				else:
					pos_in_curr_group = 1.0*r/(required_nb_elements-1)
				item_set_nb_to_pick = round(pos_in_curr_group*(actual_nb_elements-1))
				new_mts.append(elements[e][s][int(actual_nb_elements-item_set_nb_to_pick-1)])

		new_x_train.append(np.array(new_mts))
	return new_x_train

def compute_associations_by_sequence(avg_mts,x_train, dist_fun, dist_fun_params):
	"""
	This function computes all the associations between a given average
	sequence and the series in x_train
	returns a (m*n) lists
	where m is the length of the average mts
	n is the number of time series in x_train
	and the list contains the associated elements from the mts in x_train with
	the avg_mts
	"""
	n = len(x_train)
	m = avg_mts.shape[0]

	assoc_by_seq = [[[] for i in range(n)] for j in range(m)]
	for idx_series in range(n):
		mts = x_train [idx_series]
		# get the dtw alignment with the average
		dtw_dist, dtw = dist_fun(avg_mts, mts,**dist_fun_params)
		# get the association array
		i = dtw.shape[0] - 1
		j = dtw.shape[1] - 1

		permute = False
		if n + 1 == dtw.shape[1]:
			permute = True

		while i >= 1 and j >= 1:

			if permute == False:
				assoc_by_seq[j - 1][idx_series].append(mts[i - 1])
			else:
				assoc_by_seq[i - 1][idx_series].append(mts[j - 1])

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
	return assoc_by_seq

def compute_associations_by_sequence_with_index(avg_mts,x_train, dist_fun, dist_fun_params):
	"""
	This function computes all the associations between a given average
	sequence and the series in x_train
	returns a (m*n) lists
	where m is the length of the average mts
	n is the number of time series in x_train
	and the list contains the associated index of elements from the mts
	in x_train with the avg_mts
	"""
	n = len(x_train)
	m = avg_mts.shape[0]

	assoc_by_seq = [[[] for i in range(n)] for j in range(m)]
	for idx_series in range(n):
		mts = x_train [idx_series]
		# get the dtw alignment with the average
		dtw_dist, dtw = dist_fun(avg_mts, mts,**dist_fun_params)
		# get the association array
		i = dtw.shape[0] - 1
		j = dtw.shape[1] - 1

		permute = False
		if n + 1 == dtw.shape[1]:
			permute = True

		while i >= 1 and j >= 1:

			if permute == False:
				assoc_by_seq[j - 1][idx_series].append(i - 1)
			else:
				assoc_by_seq[i - 1][idx_series].append(j - 1)

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
	return assoc_by_seq