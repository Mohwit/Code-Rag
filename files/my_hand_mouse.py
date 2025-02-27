import time
import cv2
import mediapipe
import pyautogui
import numpy as np
import my_hand_mouse_utils
import matlabimport matlabimport matlabimport numpy as np
import my_hand_mouse_utils
import time
import cv2
import mediapipe
import pyautogui
import numpy as np
import my_hand_mouse_utils 

max_screen_distance = 10   # Max distance from screen using different units
min_drag_distance_left = min_drag_distance_right = 100
last_point = None


capture_hands = mediapipe.solutions.hands.Hands()
drawing_option = mediapipe.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
camera = cv2.VideoCapture(0)

hand_points = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]  # IDs -> 4,8,9,12,16,20,0,1,17   https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker



while True:
    _,image = camera.read()
    image_height, image_width, _ = image.shape
    image = cv2.flip(image,1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output_hands = capture_hands.process(rgb_image)
    all_hands = output_hands.multi_hand_landmarks 
    if all_hands:
        for hand in all_hands:
            drawing_option.draw_landmarks(image,hand)
            one_hand_landmarks = hand.landmark
            
            my_hand_mouse_utils.fill_hand_points(image, one_hand_landmarks, image_width, image_height, screen_width, hand_points)

        click_control = hand_points[0][1] - hand_points[1][1]       # Index and thumb fingers proximity.

        #print (my_hand_mouse_utils.euclidean_distance(hand_points[-1], hand_points[-2]))
        caliberator__distance = my_hand_mouse_utils.euclidean_distance(hand_points[-1], hand_points[-2])
        
        if caliberator__distance <= max_screen_distance:
            text = "TOO FAR"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 3  # Larger scale for bigger text
            color = (0, 0, 255)  # Red color in BGR
            thickness = 5

            # Get the text size to calculate the center position
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = (image.shape[1] - text_size[0]) // 2  # Center X-coordinate
            text_y = (image.shape[0] + text_size[1]) // 2  # Center Y-coordinate
            # Put text on the image
            cv2.putText(image, text, (text_x, text_y), font, font_scale, color, thickness)


        elif (my_hand_mouse_utils.is_tip_below_knuckle(hand_points)):
            # Introduce a delay before deciding the drag direction
            direction,last_point = my_hand_mouse_utils.decide_drag_direction(hand_points,min_drag_distance_left, min_drag_distance_right, last_point)
            # print (direction)
            if direction:  # If a direction was detected
                my_hand_mouse_utils.switch_desktop(direction)  # Change desktop based on drag direction

        elif (click_control < 0.20 * caliberator__distance ):
            pyautogui.click()

        
        else :
            last_point = None

    

    cv2.imshow("Hand Movement Video Capture ", image)
    key = cv2.waitKey(100)
    if key == 27:
        break
camera.release()
cv2.destroyAllWindows()