import cv2
import numpy as np
import time
import torch
import torch.nn as nn
import torchvision
from torchvision import models, transforms
from PIL import Image
import os

# ---------- Classification Model Setup ----------
def load_classification_model(model_path, num_classes, device):
    """
    Loads a MobileNet_V3_Small model pre-trained on ImageNet, replaces its classifier head
    to predict the specified number of classes, loads the fine-tuned weights, and moves
    it to the specified device.
    """
    # model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model

def load_label_mapping(data_root='images'):
    """
    Scans the given data_root directory for subdirectories (categories) and returns
    a mapping from class index to label.
    """
    categories = sorted([
        d for d in os.listdir(data_root)
        if os.path.isdir(os.path.join(data_root, d))
    ])
    label_to_idx = {category: i for i, category in enumerate(categories)}
    idx_to_label = {i: category for category, i in label_to_idx.items()}
    return idx_to_label

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Assume binary classification: 0 -> Non-Recyclable, 1 -> Recyclable
idx_to_label = load_label_mapping(data_root='images')
num_classes = 30
# model_path = './best_model_mobileNetV3_S.pth'  # Path to your fine-tuned model weights
model_path = './best_model_efficientnet_v2_s.pth'  # Path to your fine-tuned model weights

# Get the standard preprocessing transforms from the MobileNetV3 weights.
# preprocess = models.MobileNet_V3_Small_Weights.IMAGENET1K_V1.transforms()
preprocess = models.EfficientNet_V2_S_Weights.IMAGENET1K_V1.transforms()

# Load the classification model.
clf_model = load_classification_model(model_path, num_classes, device)

# ---------- Optical Flow & Deposit Detection Setup ----------
cap = cv2.VideoCapture(0)

# Capture the first frame as the baseline.
ret, baseline_frame = cap.read()
if not ret:
    print("Failed to capture baseline frame!")
    cap.release()
    exit()

baseline_gray = cv2.cvtColor(baseline_frame, cv2.COLOR_BGR2GRAY)

# Use the first frame as the previous frame for optical flow.
prev_frame = baseline_frame.copy()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# Create an HSV mask for optical flow visualization.
hsv_mask = np.zeros_like(prev_frame)
hsv_mask[..., 1] = 255  # Set saturation to maximum.

# Parameters.
motion_threshold = 5.0        # Minimum flow magnitude (in pixels) for motion.
min_contour_area = 500        # Minimum contour area to consider as valid motion.
settle_duration = 1.0         # Seconds to wait for motion to settle.
alpha = 0.05                   # Weight for background updating.

# For temporal filtering of deposit detections.
consecutive_detection_frames = 0
detection_required_frames = 3  # Require detection in 3 consecutive frames

deposit_in_progress = False
last_motion_time = None
previous_deposits = []  # List to store previous deposit bounding boxes

# Create the KNN background subtractor.
# You can tune the parameters such as history and dist2Threshold for your application.
bg_subtractor = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400.0, detectShadows=False)

while input("Press x") != 'x':
    pass

print("Press 'q' to exit.")
fg_mask_clean = np.zeros_like(baseline_gray)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if gray is None or gray.size == 0:
        print("Warning: Gray frame is empty!")
        continue

    # --- Optical Flow Calculation for Motion Detection ---
    blurred_prev = cv2.GaussianBlur(prev_gray, (5, 5), 0)
    blurred_gray = cv2.GaussianBlur(gray, (5, 5), 0)

    flow = cv2.calcOpticalFlowFarneback(
        blurred_prev, blurred_gray, None,
        pyr_scale=0.5,
        levels=3,
        winsize=25,
        iterations=5,
        poly_n=7,
        poly_sigma=1.5,
        flags=0
    )
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    # Adaptive thresholding for motion detection.
    motion_threshold_adaptive = np.mean(mag) + 2 * np.std(mag)
    motion_mask = mag > max(motion_threshold, motion_threshold_adaptive)
    motion_visual = np.uint8(motion_mask * 255)
    
    # Morphological operations to improve motion mask.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    motion_visual = cv2.morphologyEx(motion_visual, cv2.MORPH_CLOSE, kernel)
    motion_visual = cv2.morphologyEx(motion_visual, cv2.MORPH_OPEN, kernel)

    # Find contours in the motion mask.
    contours, _ = cv2.findContours(motion_visual, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:
            motion_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    current_time = time.time()
    if motion_detected:
        deposit_in_progress = True
        last_motion_time = current_time
        cv2.putText(frame, 'Motion Detected!', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Reset the deposit detection counter when motion is ongoing.
        consecutive_detection_frames = 0
    else:
        # If motion has settled for the settle_duration, run deposit detection.
        if deposit_in_progress and last_motion_time and (current_time - last_motion_time > settle_duration):
            # --- KNN Background Subtraction ---
            fg_mask = bg_subtractor.apply(gray)
            if fg_mask is not None and fg_mask.size > 0:
                fg_mask_clean = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
                fg_mask_clean = cv2.morphologyEx(fg_mask_clean, cv2.MORPH_CLOSE, kernel)
            else:
                print("Warning: fg_mask is invalid, skipping processing.")
            fg_mask_clean = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask_clean = cv2.morphologyEx(fg_mask_clean, cv2.MORPH_CLOSE, kernel)
            
            diff_contours, _ = cv2.findContours(fg_mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            deposit_found = False
            for cnt in diff_contours:
                if cv2.contourArea(cnt) > min_contour_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    # Check against previous deposits to avoid repeated registration.
                    collision_detected = any(
                        abs(px - x) < w and abs(py - y) < h for (px, py, pw, ph) in previous_deposits
                    )
                    if not collision_detected:
                        consecutive_detection_frames += 1
                        # Only register the deposit after several consecutive frames.
                        if consecutive_detection_frames >= detection_required_frames:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                            cv2.putText(frame, 'Deposit Detected!', (10, 60),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                            print('Deposit detected at ({}, {})'.format(x, y))
                            
                            # Extract the ROI for classification.
                            deposit_roi = frame[y:y+h, x:x+w]
                            cv2.imwrite(f'./deposit_roi_{int(current_time)}.png', deposit_roi)
                            
                            # --- Classification of the Deposit ROI ---
                            roi_rgb = cv2.cvtColor(deposit_roi, cv2.COLOR_BGR2RGB)
                            roi_pil = Image.fromarray(roi_rgb)
                            roi_tensor = preprocess(roi_pil).unsqueeze(0).to(device)
                            
                            with torch.no_grad():
                                output = clf_model(roi_tensor)
                                pred = output.argmax(dim=1).item()
                                predicted_label = idx_to_label.get(pred, "Unknown")
                            
                            cv2.putText(frame, f'Class: {predicted_label}', (x, y-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                            print(f'Classified deposit as: {predicted_label}')
                            
                            deposit_found = True
                            previous_deposits.append((x, y, w, h))
                            # Once a deposit is registered, exit the contour loop.
                            break
                    else:
                        # Reset the counter if the contour collides with a previous deposit.
                        consecutive_detection_frames = 0
            if deposit_found:
                deposit_in_progress = False
                consecutive_detection_frames = 0

    # --- Optical Flow Visualization ---
    hsv_mask[..., 0] = ang * 180 / np.pi / 2
    hsv_mask[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    flow_bgr = cv2.cvtColor(hsv_mask, cv2.COLOR_HSV2BGR)

    # --- Display Results ---
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Optical Flow', flow_bgr)
    cv2.imshow('Motion Mask', motion_visual)
    if fg_mask_clean is not None and fg_mask_clean.size > 0:
        cv2.imshow('KNN Foreground Mask', fg_mask_clean)

    # Update the previous frame.
    prev_gray = gray.copy()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()