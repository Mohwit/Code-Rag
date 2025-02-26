import cv2
import mediapipe
import pyautogui
import time
import numpy as np
import pytesseract
import my_hand_mouse_utils
import easyocr
import pygame

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
color = (0, 255, 255)  # Yellow color
thickness = 1

def fill_hand_points(image, one_hand_landmarks, image_width, image_height, screen_width, hand_points):
    # Define the mapping of landmark IDs to hand_points indices
    id_to_index = {
        4: 0,    # Thumb.
        8: 1,    # Forefinger.
        12: 2,   # Middle finger.
        16: 3,   # Ring finger.
        20: 4,   # Little finger.
        0: 5,    # Wrist or base.
        7: 6,    # Index knuckle  
        11: 7,   # Middle Finger Knuckle 
        9: 8,    # Middle finger bottom.    
        1: 9,    # For distance caliberation
        17: 10    # For distance caliberation
    }

    # Iterate through landmarks
    for id, lm in enumerate(one_hand_landmarks):
        x = int(lm.x * image_width)
        y = int(lm.y * image_height)
        
        # Draw circle on the image
        # if id == 12 or id == 11:
        #     cv2.circle(image, (x, y), 10, (0, 255, 255), -1)
        #     cv2.putText(image, str(id), (x + 10, y - 10), font, font_scale, color, thickness)

        # Update hand_points based on the IDs
        if id in id_to_index:
            index = id_to_index[id]
            hand_points[index] = [x, y]
            
            if id == 9:  # Middle finger base
                mouse_x = int(screen_width / image_width * x)
                mouse_y = int(screen_width / image_width * y)
                pyautogui.moveTo(mouse_x, mouse_y)
        

        # print ([euclidean_distance(hand_points[0],hand_points[1])] , euclidean_distance(hand_points[-1],hand_points[-2]))


def euclidean_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)




def is_tip_below_knuckle(hand_1):
    return (hand_1[7][1] < hand_1[2][1] and hand_1[1][1] > hand_1[6][1] )


def switch_desktop(direction):
    """Switch desktops using keyboard shortcuts."""
    if direction == 'left':
        pyautogui.hotkey('ctrl', 'left')  # Switch to the left desktop
    elif direction == 'right':
        pyautogui.hotkey('ctrl', 'right')  # Switch to the right desktop

def decide_drag_direction(hand_points, min_drag_distance_left, min_drag_distance_right ,last_point):
    """Decide the drag direction based on hand points and distance thresholds."""
    if len(hand_points) < 2:
        return None,None  # Not enough points to determine direction
    if last_point == None:
        return None,hand_points[6]

    current_point = hand_points[6]


    dist = euclidean_distance(last_point, current_point)

    # Check if the distance meets either left or right drag thresholds
    if dist >= min_drag_distance_left or dist >= min_drag_distance_right:
        delta_x = last_point[0] - current_point[0]
        if abs(delta_x) > abs(last_point[1] - current_point[1]):  # Horizontal drag
            if delta_x < 0:
                return 'right',None  # Dragging right
            else:
                return 'left',None  # Dragging left

    return None,current_point  # No valid drag detected



def ocr_from_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Check if the image is loaded
    if image is None:
        print("Error: Image not loaded. Check the path:", image_path)
        return ""

    # Create an EasyOCR Reader
    reader = easyocr.Reader(['en'])  # Specify languages; 'en' for English

    # Perform OCR
    result = reader.readtext(image)

    # Extract and print detected text
    detected_text = " ".join([text[1] for text in result])
    print("Detected Text:", detected_text)
    return detected_text

# Example usage
ocr_from_image('/Users/psinha/Desktop/testing_2 .jpg')


