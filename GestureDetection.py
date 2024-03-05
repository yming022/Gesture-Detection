import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)

result = cv2.VideoWriter('result.mp4',
cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 
15, (1068,600),4)

hands = mp.solutions.hands.Hands()
exist, image = cap.read()
height, width, channels = image.shape
x_coordinates =[]
y_coordinates =[]
previous_wrist_x = 0
wrist_x = 0
previous_tips_x =[0,0,0,0,0]
tips_x =[]
tips_y =[]
pips_x =[]
pips_y =[]
pips_coordinates =[]
hand_center_x = 0
hand_center_y = 0
centers = []
i = 0
text = ""
wave_start = time.time()
wave_end = time.time()

while cap.isOpened():

    try:
        exist, image = cap.read()
        colored_image = cv2.cvtColor(image, 4)
        hand_lms_exist = hands.process(colored_image).multi_hand_landmarks

    except Exception:
        print("The video has ended, so the window is closed.")
        break

    if hand_lms_exist:
        for handLMs in hand_lms_exist:
            for lm in handLMs.landmark:

                x_coordinates.append(int(lm.x * width) ) 
                y_coordinates.append(int(lm.y * height) )
                        
            start_x = min(x_coordinates)
            start_y = min(y_coordinates)
            end_x = max(x_coordinates)
            end_y = max(y_coordinates)

# Draw rectangle

            cv2.rectangle(image, (start_x - 10, start_y - 10), 
            (end_x + 10, end_y + 10), (0, 255, 0), 2)

# Draw tracking line

            hand_center_x = round((start_x + end_x)/2)
            hand_center_y = round((start_y + end_y)/2)
            centers.append((hand_center_x, hand_center_y))
            while(i+2<len(centers)):
                x1, y1 = centers[i]
                x2, y2 = centers[i+2]
                a = x1-x2
                b = y1-y2
                if (abs(b)>100 or abs(a)>100):
                        i += 1
                        pass
                else:
                        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 4,1)
                        i += 1
            i = 1

# Get the landmarks to help the detection of the gestures.

            while(i<6):
                tips_x.append(x_coordinates[4*i])
                tips_y.append(y_coordinates[4*i])
                pips_x.append(x_coordinates[4*i-2])
                pips_y.append(y_coordinates[4*i-2])
                i += 1
            i = 0
            wrist_x = x_coordinates[0]


# Define the gestures.
            waving = True
            while(i<5):
                if (abs(tips_x[i] - previous_tips_x[i]) <= 
                abs(wrist_x - previous_wrist_x) + 10):
                      waving = False                           
                i += 1
            i = 1

            fisting = True
            while(i<5):
                if (tips_y[i] < pips_y[i] or 
                (tips_x[0] > pips_x[1] and tips_x[0] > pips_x[4] ) or
                (tips_x[0] < pips_x[1] and tips_x[0] < pips_x[4] )):
                        fisting = False                          
                i += 1
            i = 0
            
            number = True
            value = ""
            if (tips_y[1] > pips_y[1]):
                    number = False    
            elif (tips_y[2] > pips_y[2]):
                    value = "1"  
            elif (tips_y[3] > pips_y[3]):
                    value = "2"  
            elif (tips_y[4] > pips_y[4]):
                    value = "3"  
            elif ( (tips_x[0] < pips_x[1] and tips_x[0] > pips_x[4] ) or
                (tips_x[0] > pips_x[1] and tips_x[0] < pips_x[4] )):
                    value = "4"  
            else:
                    value = "5"  

# Identify the gesture.

            if (waving):
                        wave_start = time.time()
                        text = "Wave"
            elif (number):
                        wave_end = time.time()
                        if (wave_end - wave_start >= 1):
                                    text = "Number: " + value
            elif (fisting):
                        text = "Fist"
            else:
                        wave_end = time.time()
                        if (wave_end - wave_start >= 1):
                                    text = "Thumb"

# Write text and reset the variables.

            cv2.putText(image,text, (start_x, start_y - 20), 
            cv2.FONT_ITALIC, 1, (0,255,255),2)
            while(i<5):
                previous_tips_x[i] = tips_x[i]
                i += 1
            i = 0
            previous_wrist_x = wrist_x
            x_coordinates =[]
            y_coordinates =[]
            tips_x =[]
            tips_y =[]
            pips_x =[]
            pips_y =[]

    cv2.imshow("Hand Detection and Motion Tracking", image)
    result_image = cv2.resize(image,(1068,600))
    result.write(result_image) 
    out = cv2.waitKey(1)
    if out == 32:
        break	


cap.release()
result.release()