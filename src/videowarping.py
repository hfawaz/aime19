import cv2
import numpy as np
import csv



def videowarping(originalvideo_1_path, originalvideo_2_path, frameduration_video_1, frameduration_video_2, warpedvideopath):

    original_video_1 = cv2.VideoCapture(originalvideo_1_path)
    original_video_2 = cv2.VideoCapture(originalvideo_2_path)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    warpedvideo = cv2.VideoWriter(warpedvideopath, fourcc, original_video_1.get(cv2.CAP_PROP_FPS), (1280, 480))

    #computer frames number of final video
    n, m = np.unique(frameduration_video_1, return_counts=True)
    framecount=0
    for i in range(0, len(n)):
        framecount+=n[i]*m[i]
    framecount=np.int(framecount)

    warpedframes = np.zeros((2, framecount), dtype=int)

    warpedframe=0
    for frame in range(0, len(frameduration_video_1)):
        for i in range(0, np.int(frameduration_video_1[frame][0])):
            warpedframes[0][warpedframe]=frame
            warpedframe+=1

    warpedframe = 0
    for frame in range(0, len(frameduration_video_2)):
        for i in range(0, np.int(frameduration_video_2[frame][0])):
            warpedframes[1][warpedframe] = frame
            warpedframe += 1


    #Video alignment
    currentframeindex_video_1 = -10000
    currentframeindex_video_2 = -10000
    for frame in range(0, len(warpedframes[0])):
        if currentframeindex_video_1 < warpedframes[0][frame]:
            currentframeindex_video_1 = warpedframes[0][frame]
            ret1, currentframe_video_1 = original_video_1.read()
            # if videos is 320x240 instead of 640x480 (yes it happens)
            (x1, y1, b1) = currentframe_video_1.shape
            if x1 == 240:
                currentframe_video_1 = cv2.resize(currentframe_video_1, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        if currentframeindex_video_2 < warpedframes[1][frame]:
            currentframeindex_video_2 = warpedframes[1][frame]
            ret2, currentframe_video_2 = original_video_2.read()
            # if videos is 320x240 instead of 640x480 (yes it happens)
            (x2, y2, b2) = currentframe_video_2.shape
            if x2 == 240:
                currentframe_video_2 = cv2.resize(currentframe_video_2, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        currentframe = np.concatenate((currentframe_video_1,currentframe_video_2), axis=1)

        warpedvideo.write(currentframe)

    original_video_1.release()
    original_video_2.release()
    warpedvideo.release()

    return

# only for 2x2, need some generalization
def multiplevideowarping(rootpath, surgerytype, surgeries, videowarpingvectors, warpedvideopath):

    dictgestures = {}
    dictgestures["G0"] = "No gesture"
    dictgestures["G1"] = "Reaching for needle with right hand"
    dictgestures["G2"] = "Positioning needle"
    dictgestures["G3"] = "Pushing needle through tissue"
    dictgestures["G4"] = "Transferring needle from left to right"
    dictgestures["G5"] = "Moving to center with needle in grip"
    dictgestures["G6"] = "Pulling suture with left hand"
    dictgestures["G7"] = "Pulling suture with right hand"
    dictgestures["G8"] = "Orienting needle"
    dictgestures["G9"] = "Using right hand to help tighten suture"
    dictgestures["G10"] = "Loosening more suture"
    dictgestures["G11"] = "Dropping suture at end and moving to end points"
    dictgestures["G12"] = "Reaching for needle with left hand"
    dictgestures["G13"] = "Making C loop around right hand"
    dictgestures["G14"] = "Reaching for suture with right hand"
    dictgestures["G15"] = "Pulling suture with both hands"

    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 470)
    fontScale = 1
    fontColor = (255, 255, 255)
    lineType = 2

    originalvideos = []
    for i in range(len(surgeries)):
        originalvideos.append(cv2.VideoCapture(rootpath+surgerytype+'_video/video/'+surgeries[i]+'_capture1.avi'))

    gestures = []
    for i in range(len(surgeries)):
        numberofframes=int(originalvideos[i].get(cv2.CAP_PROP_FRAME_COUNT))
        with open(rootpath + surgerytype + '_kinematic/transcriptions/' + surgeries[i] + '.txt', newline='') as csvfile:
            gesturereader = csv.reader(csvfile, delimiter=' ')
            tmp=[]
            for row in gesturereader:
                tmp.append(row)
            videogesture = []
            currentgesturemin = int(tmp[0][0])
            currentgesturemax = int(tmp[0][1])
            currentgesture = tmp[0][2]
            rowindex=0
            for frame in range(numberofframes):
                if frame < currentgesturemin: #no gesture yet
                    videogesture.append("G0")
                elif frame <= currentgesturemax:
                    videogesture.append(currentgesture)
                    if frame == currentgesturemax:
                        rowindex += 1
                        if rowindex < len(tmp):
                            currentgesturemin = int(tmp[rowindex][0])
                            currentgesturemax = int(tmp[rowindex][1])
                            currentgesture = tmp[rowindex][2]
                else: #no more gestures
                    videogesture.append("G0")
        gestures.append(videogesture)


    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    if len(surgeries) == 4:
        warpedvideo = cv2.VideoWriter(warpedvideopath, fourcc, originalvideos[0].get(cv2.CAP_PROP_FPS), (1280, 960))
    else:
        warpedvideo = cv2.VideoWriter(warpedvideopath, fourcc, originalvideos[0].get(cv2.CAP_PROP_FPS), (1920, 1440))

    #computer frames number of final video
    n, m = np.unique(videowarpingvectors[surgeries[0]], return_counts=True)
    framecount = 0
    for i in range(0, len(n)):
        framecount += n[i]*m[i]
    framecount = np.int(framecount)

    for surgery in range(len(surgeries)):
        n, m = np.unique(videowarpingvectors[surgeries[surgery]], return_counts=True)
        framecount = 0
        for i in range(0, len(n)):
            framecount += n[i] * m[i]
        framecount = np.int(framecount)
        print(surgery)
        print(framecount)


    warpedframes = np.zeros((len(surgeries), framecount), dtype=int)

    currentframeindex = [-1]*len(surgeries)
    currentframe = [None]*len(surgeries)
    still = [False]*len(surgeries)

    for surgery in range(len(surgeries)):
        warpedframe=0
        for frame in range(len(videowarpingvectors[surgeries[surgery]])):
            for i in range(np.int(videowarpingvectors[surgeries[surgery]][frame][0])):
                warpedframes[surgery][warpedframe] = frame
                warpedframe += 1

    print(warpedframes[0])

    currentframeinoriginalvideo = [-1]*len(surgeries)

    #Video alignment
    for frame in range(0, len(warpedframes[0])):
        for surgery in range(len(surgeries)):
            if currentframeindex[surgery] < warpedframes[surgery][frame]:
                still[surgery]=False
                currentframeindex[surgery] = warpedframes[surgery][frame]
                ret, currentframe[surgery] = originalvideos[surgery].read()
                currentframeinoriginalvideo[surgery]+=1
                # if videos are 320x240 instead of 640x480 (yes it happens)
                (x, y, b) = currentframe[surgery].shape
                if x == 240:
                    currentframe[surgery] = cv2.resize(currentframe[surgery], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                cv2.putText(currentframe[surgery], dictgestures[gestures[surgery][currentframeinoriginalvideo[surgery]]],
                            bottomLeftCornerOfText,
                            font,
                            fontScale,
                            fontColor,
                            lineType)
            else:
                if still[surgery] == False:
                    still[surgery] = True
                    currentframe[surgery] = cv2.cvtColor(currentframe[surgery], cv2.COLOR_BGR2GRAY)
                    currentframe[surgery] = np.repeat(currentframe[surgery][:, :, np.newaxis], 3, axis=2)

        if len(surgeries) == 4:
            currentframeH1 = np.concatenate((currentframe[0], currentframe[1]), axis=1)
            currentframeH2 = np.concatenate((currentframe[2], currentframe[3]), axis=1)
            currentframeglobal = np.concatenate((currentframeH1, currentframeH2), axis=0)
        else:
            currentframeH1 = np.concatenate((currentframe[0], currentframe[1], currentframe[2]), axis=1)
            currentframeH2 = np.concatenate((currentframe[3], currentframe[4], currentframe[5]), axis=1)
            currentframeH3 = np.concatenate((currentframe[6], currentframe[7], currentframe[8]), axis=1)
            currentframeglobal = np.concatenate((currentframeH1, currentframeH2, currentframeH3), axis=0)

        warpedvideo.write(currentframeglobal)
    for surgery in range(len(surgeries)):
        originalvideos[surgery].release()
    warpedvideo.release()

    return



