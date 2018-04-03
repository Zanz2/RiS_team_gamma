import cv2
import numpy as np

#cv_image = bridge.imgmsg_to_cv2(data, "bgr8")

sizeX = 3840/6
sizeY = 2160/6

cv_image = cv2.imread('Img.jpg')

cv_image = cv2.resize(cv_image,(sizeX, sizeY), interpolation=cv2.INTER_CUBIC)

cv_image = cv_image[sizeY/4:(sizeY/4)*3, 0:sizeX]

# Set the dimensions of the image
dims = cv_image.shape

# Tranform image to gayscale
gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

# Do histogram equlization
img = cv2.equalizeHist(gray)

thresholds = []
# Binarize the image

for tr in range(20, 141, 15):
    ret, thresh = cv2.threshold(img, tr, 255, 0)
    thresholds.append(thresh)
    cv2.imshow("Image window", thresh)
    cv2.waitKey(0)

'''
cv2.imshow("Image window", thresh)
cv2.waitKey(0)

cv2.imshow("Image window", thresh2)
cv2.waitKey(0)

cv2.imshow("Image window", thresh3)
cv2.waitKey(0)
'''

# Extract contours
allContours = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
for i, thresh in enumerate(thresholds):
    contours, hierarchy = cv2.findContours(thresh, 2, 2)
    for contoure in contours:
        allContours[i].append(contoure)


elpses = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
for i, contoure in enumerate(allContours):
    for cnt in contoure:
        #     print cnt
        #     print cnt.shape
        if cnt.shape[0] >= 20:
            ellipse = cv2.fitEllipse(cnt)
            elpses[i].append(ellipse)

candidates = []

for elps in elpses:
    #print("---")
    for n in range(len(elps)):
        #i = 0
        for m in range(n + 1, len(elps)):

            e1 = elps[n]
            e2 = elps[m]
            dist = np.sqrt(((e1[0][0] - e2[0][0]) ** 2 + (e1[0][1] - e2[0][1]) ** 2))
            pos = (((e1[0][0] + e2[0][0])/2), ((e1[0][1] + e2[0][1])/2))


            try:
                razmerje = e1[1][0] / e2[1][0]
                razmerje2 = e1[1][1] / e2[1][1]
            except:
                break

            if dist < 5 and ((razmerje < 1.5 and razmerje > 1.1) or (razmerje < 0.9 and razmerje > 0.6))and ((razmerje2 < 1.5 and razmerje2 > 1.1) or (razmerje2 < 0.9 and razmerje2 > 0.6)) and pos[1] > sizeY/2/4 and pos[1] < (sizeY/2/4)*3:
                #i += 1
                #if i==2:
                #print (pos)
                candidates.append((e1,e2, pos))
                    #print(n, " ", m)
                #    break
            #sredisce na polovici
'''
print("---------")

for c in candidates:
    print(c)

print("---------")
'''
realCandidates = []
used = []
for n in range(len(candidates)):
    for m in range(n+1, len(candidates)):

        e1 = candidates[n]
        e2 = candidates[m]

        if abs(e1[2][0]-e2[2][0]) < 5 and abs(e1[2][1]-e2[2][1]) < 5:
            if n not in used and m not in used:
                realCandidates.append(e1)

            used.append(n)
            used.append(m)
            #candidates[m] = False
            #print(n, " ", m)
            break

for c in realCandidates:
    print(c)

    e1 = c[0]
    e2 = c[1]

    cv2.ellipse(cv_image, e1, (0, 255, 0), 2)
    cv2.ellipse(cv_image, e2, (0, 255, 0), 2)

    size = (e1[1][0]+e1[1][1])/2
    center = (e1[0][1], e1[0][0])

    x1 = int(center[0] - size / 2)
    x2 = int(center[0] + size / 2)
    x_min = x1 if x1>0 else 0
    x_max = x2 if x2<cv_image.shape[0] else cv_image.shape[0]

    y1 = int(center[1] - size / 2)
    y2 = int(center[1] + size / 2)
    y_min = y1 if y1 > 0 else 0
    y_max = y2 if y2 < cv_image.shape[1] else cv_image.shape[1]

    #depth_image = bridge.imgmsg_to_cv2(depth_img, "16UC1")

    #get_pose(e1, float(np.mean(depth_image[x_min:x_max,y_min:y_max,:]))/1000.0)


cv2.imshow("Image window",cv_image)
cv2.waitKey(0)