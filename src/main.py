import numpy as np
import time
from keras.utils import np_utils
import os
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import collections
import re
import matplotlib
matplotlib.use('pdf')
import sys
from dba import dba
from nlts import compute_associations_by_sequence_with_index
from videowarping import multiplevideowarping
from videowarping import videowarping
from distances.dtw.dtw import  dynamic_time_warping as dtw

def getExpertiseLevelOfSurgery(surgery_name,surgeries_metadata):
	## function getMetaDataForSurgeries should be already called
	if surgeries_metadata.__contains__(surgery_name):
		return surgeries_metadata[surgery_name][0]
	return None

def getMetaDataForSurgeries(surgery_type):
	surgeries_metadata = {}
	file = open(root_dir+surgery_type+'_kinematic/'+'meta_file_'+surgery_type+'.txt','r')
	for line in file:
		line = line.strip() ## remove spaces

		if len(line)==0: ## if end of file
			break

		b = line.split()
		surgery_name = b[0]
		expertise_level = b[1]
		b = b[2:]
		scores = [int(e) for e in b]
		surgeries_metadata[surgery_name]=(expertise_level,scores)
	return surgeries_metadata

def fit_encoder(y_train,y_test,y_val): 
	y_train_test_val = y_train+y_test+y_val
	encoder.fit(y_train_test_val)

def convertStringClassesToBinaryClasses(y_train,y_test,y_val):
	idx_y_test = len(y_train)
	idx_y_val = len(y_train)+len(y_test)
	y_train_test_val = y_train+y_test+y_val
	# encoder.fit(y_train_test)
	y_train_test_val = encoder.transform(y_train_test_val)
	y_train_test_val = np_utils.to_categorical(y_train_test_val)
	y_train = y_train_test_val[0:idx_y_test]
	y_test = y_train_test_val[idx_y_test:idx_y_val]
	y_val = y_train_test_val[idx_y_val:]
	return y_train,y_test,y_val

def get_user_name_and_trial_num(surgery_name,surgery_type):
	user_name = surgery_name.replace(surgery_type+'_',"")[0]
	trial_num = surgery_name.replace(surgery_type+'_',"")[-1]
	return user_name,trial_num

def readFile(file_name,dtype,columns_to_use=None):
	X = np.loadtxt(file_name,dtype,usecols=columns_to_use)
	return X

def generateMaps(surgery_type, return_meta_data=False):
	surgeries_metadata = getMetaDataForSurgeries(surgery_type)
	mapSurgeryDataBySurgeryName = collections.OrderedDict() # indexes surgery data (76 dimensions) by surgery name
	mapExpertiseLevelBySurgeryName = collections.OrderedDict() # indexes exerptise level by surgery name
	listOfSurgeries =[]
	y =[]
	path = root_dir+surgery_type+'_kinematic'+'/kinematics/AllGestures/'
	for subdir,dirs,files in os.walk(path):
		for file_name in files:
			surgery = readFile(path+file_name,float,columns_to_use=dimensions_to_use)
			surgery_name = file_name[:-4]
			expertise_level = getExpertiseLevelOfSurgery(surgery_name,surgeries_metadata)
			if expertise_level is None:
				continue
			mapSurgeryDataBySurgeryName[surgery_name] = surgery
			mapExpertiseLevelBySurgeryName[surgery_name] = expertise_level
			mapGesturesBySurgeryName = generateGesturesForSurgery(surgery_name,surgery_type,mapSurgeryDataBySurgeryName)

	if return_meta_data == True:
		return mapSurgeryDataBySurgeryName,mapExpertiseLevelBySurgeryName,mapGesturesBySurgeryName, surgeries_metadata
	else:
		return mapSurgeryDataBySurgeryName, mapExpertiseLevelBySurgeryName, mapGesturesBySurgeryName

def generateGesturesForSurgery(surgery_name, surgery_type,mapSurgeryDataBySurgeryName):
	mapGesturesBySurgeryName = collections.OrderedDict() # indexes gestures of a surgery by its name
	surgery = mapSurgeryDataBySurgeryName[surgery_name]
	path = root_dir+ surgery_type+'_kinematic/transcriptions/'
	file_name = surgery_name + '.txt'
	data = readFile(path+file_name,str)
	gestures = []

	for row in data:
		start_index = int(row[0]) -1
		end_index = int(row[1])
		gesture_name = row[2]
		gestures.append((gesture_name,surgery[start_index:end_index],start_index,end_index))

	mapGesturesBySurgeryName[surgery_name] = gestures
	return mapGesturesBySurgeryName

def find_pattern(word,pattern):
	return re.search(r''+pattern,word).group(0)

def dtw_synch(surgery_name_1,surgery_name_2,
			  mapSurgeryDataBySurgeryName, retur_score=False):
	# get the mts for surgery 1
	mts_1_left = mapSurgeryDataBySurgeryName[surgery_name_1][:,38:41]
	mts_1_right = mapSurgeryDataBySurgeryName[surgery_name_1][:,57:60]
	mts_1 = np.concatenate((mts_1_left,mts_1_right),axis=1)
	vector_1 = np.zeros(shape=(mts_1.shape[0], 1))

	# get the mts for surgery 2
	mts_2_left = mapSurgeryDataBySurgeryName[surgery_name_2][:,38:41]
	mts_2_right = mapSurgeryDataBySurgeryName[surgery_name_2][:,57:60]
	mts_2 = np.concatenate((mts_2_left,mts_2_right),axis=1)
	vector_2 = np.zeros(shape=(mts_2.shape[0],1 ))

	perm = False
	# make sur mts_1 is shorter than mts_2
	if mts_1.shape[0] > mts_2.shape[0]:
		perm = True
		t = mts_1
		mts_1 = mts_2
		mts_2 = t
		t = vector_1
		vector_1 = vector_2
		vector_2 = t

	dtw_score , dtw_mat = dtw(mts_1,mts_2)

	i = vector_1.shape[0]
	j = vector_2.shape[0]

	while i>=1 and j>=1:
		vector_1[i-1] = vector_1[i-1] +1
		vector_2[j-1] = vector_2[j-1] + 1
		a = dtw_mat[i - 1, j - 1]
		b = dtw_mat[i, j - 1]
		c = dtw_mat[i - 1, j]

		if a < b:
			if a < c:
				# a is the minimum
				i -= 1
				j -= 1
			else:
				# c is the minimum
				i -= 1
		else:
			if b < c:
				# b is the minimum
				j -= 1
			else:
				# c is the minimum
				i -= 1

	if retur_score == True:
		return dtw_score

	if perm ==True:
		return vector_2,vector_1
	else:
		return vector_1,vector_2

def get_all_dtw_vectors(surgery_type):
	mapSurgeryDataBySurgeryName, _,_ = generateMaps(surgery_type)
	# returns a dictrionnary with the name of the couple of surgeries with their corresponding vectors
	# aligned with DTW
	mapDTWbySurgeryName= collections.OrderedDict()
	for surgery_name_1 in mapSurgeryDataBySurgeryName.keys():
		# get the mts
		mts_1_left = mapSurgeryDataBySurgeryName[surgery_name_1][:,38:41]
		mts_1_right = mapSurgeryDataBySurgeryName[surgery_name_1][:,57:60]
		mts_1 = np.concatenate((mts_1_left,mts_1_right),axis=1)
		vector_1 = np.zeros(shape=(mts_1.shape[0], 1))
		for surgery_name_2 in mapSurgeryDataBySurgeryName.keys():
			# do not align a sequence with itself
			if surgery_name_1==surgery_name_2:
				continue
			# since DTW is symmetric do not re-align an already aligned pair
			if (surgery_name_1+','+surgery_name_2 in mapDTWbySurgeryName) or \
					((surgery_name_2+','+surgery_name_1 in mapDTWbySurgeryName)):
				continue
			# get the mts
			mts_2_left = mapSurgeryDataBySurgeryName[surgery_name_2][:,38:41]
			mts_2_right = mapSurgeryDataBySurgeryName[surgery_name_2][:,57:60]
			mts_2 = np.concatenate((mts_2_left,mts_2_right),axis=1)
			vector_2 = np.zeros(shape=(mts_2.shape[0],1 ))

			perm = False
			# make sur mts_1 is shorter than mts_2
			if mts_1.shape[0] > mts_2.shape[0]:
				perm = True
				t = mts_1
				mts_1 = mts_2
				mts_2 = t
				t = vector_1
				vector_1 = vector_2
				vector_2 = t

			_,dtw_mat = dtw(mts_1,mts_2)

			i = vector_1.shape[0]
			j = vector_2.shape[0]

			while i>=1 and j>=1:
				vector_1[i-1] = vector_1[i-1] +1
				vector_2[j-1] = vector_2[j-1] + 1
				a = dtw_mat[i - 1, j - 1]
				b = dtw_mat[i, j - 1]
				c = dtw_mat[i - 1, j]

				if a < b:
					if a < c:
						# a is the minimum
						i -= 1
						j -= 1
					else:
						# c is the minimum
						i -= 1
				else:
					if b < c:
						# b is the minimum
						j -= 1
					else:
						# c is the minimum
						i -= 1
			if perm == False:
				mapDTWbySurgeryName[surgery_name_1+','+surgery_name_2] = (vector_1,vector_2)
			else:
				mapDTWbySurgeryName[surgery_name_1 + ',' + surgery_name_2] = (vector_2, vector_1)

	return mapDTWbySurgeryName

def get_multi_dtw_vectors(surgery_type, surgeries):
	mapSurgeryDataBySurgeryName, _, _ = generateMaps(surgery_type)

	list_of_mts = collections.OrderedDict()
	arr_of_mts = []
	# get the mts for each surgery name
	for surgery_name in surgeries:
		# get the mts
		mts_left = mapSurgeryDataBySurgeryName[surgery_name][:, 38:41]
		mts_right = mapSurgeryDataBySurgeryName[surgery_name][:, 57:60]
		mts = np.concatenate((mts_left, mts_right), axis=1)

		list_of_mts[surgery_name]=mts
		arr_of_mts.append(mts)

	# average the set of surgeries now
	avg_surg = dba(arr_of_mts)

	res = collections.OrderedDict()

	# get the distance function
	dist_fun = dtw
	# get the distance function params
	dist_fun_params = {'w':-1}

	elements = compute_associations_by_sequence_with_index(avg_surg, arr_of_mts, dist_fun, dist_fun_params)

	# get the number of training series
	n = len(arr_of_mts)
	# get the length of the average mts
	m = avg_surg.shape[0]

	# get the max number of elements associated to every element of the average sequence
	max_element_nb = np.zeros((m,), dtype=np.int64)
	for e in range(m):
		max_element_nb[e] = len(elements[e][0])
		for s in range(1, n):
			max_element_nb[e] = max(max_element_nb[e], len(elements[e][s]))

	# loop through each mts
	for s in range(n):
		surgery_name = surgeries[s]
		v = np.zeros(shape=(arr_of_mts[s].shape[0], 1))

		for e in range(m):
			required_nb_elements = max_element_nb[e]
			actual_nb_elements = len(elements[e][s])

			for r in range(required_nb_elements-1,-1,-1):
				index_offset = elements[e][s][r%actual_nb_elements]

				index_v = index_offset

				v[index_v]+=1

		res[surgery_name] = v

	return res

def get_dtw_vectors(surgery_type, surgery_name_1,surgery_name_2):
	mapSurgeryDataBySurgeryName, _, _ = generateMaps(surgery_type)

	vector_1,vector_2 = dtw_synch(surgery_name_1,surgery_name_2,mapSurgeryDataBySurgeryName)

	return vector_1,vector_2

def get_list_of_surgeries(surgery_type):
	mapSurgeryDataBySurgeryName, _, _ = generateMaps(surgery_type)
	return mapSurgeryDataBySurgeryName.keys()

def get_dtw_score_between_two_surgeries(s1, s2, mapSurgeryDataBySurgeryName):
	return dtw_synch(s1,s2,mapSurgeryDataBySurgeryName,retur_score=True)

def get_osats_score_between_two_surgeries(s1,s2,mapSurgeryDataBySurgeryName,surgery_map_metadata):
	meta_data_1 = surgery_map_metadata[s1][1]
	meta_data_2 = surgery_map_metadata[s2][1]
	# osats_score_1 = meta_data_1[0]
	# osats_score_2 = meta_data_2[0]

	res = 0

	for i in range(1,len(meta_data_2)):
		res+= np.abs(meta_data_1[i]-meta_data_2[i])

	return res

def align_videos(surgery_type_input, sur_list):

	out_vid_dir = '../out.avi'

	videowarpingvectors = get_multi_dtw_vectors(surgery_type=surgery_type_input,
													 surgeries=sur_list)

	multiplevideowarping(root_dir, surgery_type_input, sur_list,
						 videowarpingvectors, out_vid_dir)

def align_2_videos(surgery_type, s1,s2):
	originalvideo1path = root_dir + surgery_type + '_video/video/' + \
						 surgery_type + '_' + s1 + '_capture1.avi'
	originalvideo2path = root_dir + surgery_type + '_video/video/' + \
						 surgery_type + '_' + s2 + '_capture1.avi'

	vector_video_1, vector_video_2 = get_dtw_vectors(surgery_type=surgery_type,
								  surgery_name_1=surgery_type + '_' + s1,
								  surgery_name_2=surgery_type + '_' + s2)

	warpedvideopath = '../out.avi'

	videowarping(originalvideo1path, originalvideo2path, vector_video_1, vector_video_2, warpedvideopath)

#time
start_time = time.time()

# Global parameters
root_dir = '../JIGSAWS/'
dimensions_to_use = range(0,76)
classes = ['N','I','E']
nb_classes = len(classes)
confusion_matrix = pd.DataFrame(np.zeros(shape = (nb_classes,nb_classes)), index = classes, columns = classes ) # matrix used to calculate the JIGSAWS evaluation
encoder = LabelEncoder() # used to transform labels into binary one hot vectors 

if len(sys.argv) > 1:
	# input parameters
	root_dir = '../JIGSAWS/'
	surgery_type_input = sys.argv[1]
	fun_execute = sys.argv[2]

	if fun_execute == 'align_videos':
		sur_list = [surgery_type_input+'_I002', surgery_type_input+'_B003',
					surgery_type_input+'_H004', surgery_type_input+'_I003']

		align_videos(surgery_type_input, sur_list)

	elif fun_execute == 'align_2_videos':
		s1 = 'D002'
		s2 = 'G003'

		align_2_videos(surgery_type_input,s1,s2)

	print('End')