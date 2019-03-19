# JIGSAWS Video alignment based on DTW
The goal is to synch the videos based on the DTW alignement of XYZ coordianates for both robots hands. 
# Code
We have three surgical tasks in JIGSAWS. 
```
Suturing
Knot_Tying
Needle_Passing
```
To get the list of possible surgery names for a certain surgical task (e.g. Suturing) you can run: 
```
python3 src/main.py Suturing get_list_of_surgeries
```
You can also use the function ```main.get_list_of_surgeries(surgery_type='Suturing')```


To get a dictionary where each couple of surgeries for a certain surgical task (e.g. Suturing) is algined, you can run: 
```
python3 src/main.py Suturing get_all_dtw_vectors
```
Here the dictionary will contain a key for example: ```Suturing_I001,Suturing_B001``` where the surgery ```Suturing_I001``` is aligned with ```Suturing_B001```.
Every key will give two vectors (one for each surgery) 
You can also use the function ```main.get_all_dtw_vectors(surgery_type='Suturing')```


To get the alignemend for two surgeries, you can run:
```
python3 src/main.py Suturing get_dtw_vectors Suturing_I001 Suturing_B001
```
You cal also use the function ```main.get_dtw_vectors(surgery_type='Suturing',surgery_name_1='Suturing_I001',surgery_name_2='Suturing_B001')```


To align multi-videos, you can run: 
```
python3 src/main.py Suturing get_multi_dtw_vectors
```
You can also use the function 
```main.get_multi_dtw_vectors(surgery_type='Suturing', list_of_surgery_names)
``` 
