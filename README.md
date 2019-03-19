# Automatic alignment of surgical videos using kinematic data
This is the companion repository for our paper also available on ArXiv titled "Automatic alignment of surgical videos using kinematic data".
This paper has been accepted at the [Conference on Artificial Intelligence in Medicine (AIME) 2019](http://aime19.aimedicine.info/).

## Approach 
The following is an example on how a time series alignment is used to synchronize the videos by duplicating the gray-scale frames.

Video without alignment             |  Video with alignment
:-------------------------:|:-------------------------:
![unsynched](https://github.com/hfawaz/aime19/blob/master/img/ts-videos.png)  |  ![synched](https://github.com/hfawaz/aime19/blob/master/img/ts-videos-synched.png)

The following is an example of aligning coordinate X’s time series for subject F, when performing three trials of the suturing surgical task.

Time series without alignment             |  Time series with alignment
:-------------------------:|:-------------------------:
![unsynched](https://github.com/hfawaz/aime19/blob/master/img/ts-ex-original.png)  |  ![synched](https://github.com/hfawaz/aime19/blob/master/img/ts-ex-warped.png)



## Data
You will need the [JIGSAWS: The JHU-ISI Gesture and Skill Assessment Working Set](https://cirl.lcsr.jhu.edu/research/hmm/datasets/jigsaws_release/) to re-run the experiments of the paper.

Suturing |  Knot-Tying | Needle-Passing
:-------------------------:|:-------------------------:|:-------------------------:
![st](https://github.com/hfawaz/aime19/blob/master/img/su.png)  |  ![kt](https://github.com/hfawaz/aime19/blob/master/img/kt.png) | ![np](https://github.com/hfawaz/aime19/blob/master/img/np.png)

## Prerequisites
To run the code you will also need to download seperatly and install the following dependencies that can be found [here](https://github.com/hfawaz/aime19/blob/master/pip-req.txt): 
* [Keras](https://keras.io/)
* [Tensorflow](https://www.tensorflow.org/) 
* [Numpy](http://www.numpy.org/)
* [Scikit-learn](http://scikit-learn.org/stable/) 
* [Pandas](https://pandas.pydata.org/) 
* [Scikit-image](https://scikit-image.org)
* [Opencv-python](https://pypi.org/project/opencv-python/)

## Code
We have three surgical tasks in JIGSAWS. 
```
Suturing
Knot_Tying
Needle_Passing
```

To align multiple videos for the Suturing task using the NLTS algorithm, you can run:
```
python3 main.py Suturing align_videos
```

To aligne only two videos for the Suturing task using the classic DTW algorithm, you can run: 
```
python3 main.py Suturing align_2_videos
```

## Reference

If you re-use this work, please cite:

```
@InProceedings{IsmailFawaz2019automatic,
  Title                    = {Automatic alignment of surgical videos using kinematic data},
  Author                   = {Ismail Fawaz, Hassan and Forestier, Germain and Weber, Jonathan and Petitjean, François and Idoumghar, Lhassane and Muller, Pierre-Alain},
  booktitle                = {Artificial Intelligence in Medicine},
  Year                     = {2019}
}
```
