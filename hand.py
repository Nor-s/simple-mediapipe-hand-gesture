# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import cv2
import sys
import mediapipe as mp
import keyboard
import logging
import sys
import math

# %%
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG,
                    stream=sys.stdout)


def get_active_window():
    """
    Get the currently active window.

    Returns
    -------
    string :
        Name of the currently active window.
    """
    import sys
    active_window_name = None
    if sys.platform in ['linux', 'linux2']:
        # Alternatives: https://unix.stackexchange.com/q/38867/4784
        try:
            import wnck
        except ImportError:
            logging.info("wnck not installed")
            wnck = None
        if wnck is not None:
            screen = wnck.screen_get_default()
            screen.force_update()
            window = screen.get_active_window()
            if window is not None:
                pid = window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
        else:
            try:
                from gi.repository import Gtk, Wnck
                gi = "Installed"
            except ImportError:
                logging.info("gi.repository not installed")
                gi = None
            if gi is not None:
                Gtk.init([])  # necessary if not using a Gtk.main() loop
                screen = Wnck.Screen.get_default()
                screen.force_update()  # recommended per Wnck documentation
                active_window = screen.get_active_window()
                pid = active_window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
    elif sys.platform in ['Windows', 'win32', 'cygwin']:
        # https://stackoverflow.com/a/608814/562769
        import win32gui
        window = win32gui.GetForegroundWindow()
        active_window_name = win32gui.GetWindowText(window)
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        # https://stackoverflow.com/a/373310/562769
        from AppKit import NSWorkspace
        active_window_name = (NSWorkspace.sharedWorkspace()
                              .activeApplication()['NSApplicationName'])
    else:
        print("sys.platform={platform} is unknown. Please report."
              .format(platform=sys.platform))
        print(sys.version)
    return active_window_name


# %%
# 랜드마크를 그리기 위한 변수
mp_drawing = mp.solutions.drawing_utils
# 손을 처리하기 위한 변수
mp_drawing_styles = mp.solutions.drawing_styles
# 랜드마크 표시 스타일
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
# width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# print('original size: %d, %d' % (width, height))

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, width/3)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height/3)
# width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# print('changed size: %d, %d' % (width, height))


# %%
def get_angle(p1, p2, p3):
    a = math.sqrt((p1.x-p2.x)**2 + (p1.y -p2.y)**2)
    b = math.sqrt((p3.x-p2.x)**2 + (p3.y -p2.y)**2)
    c = math.sqrt((p1.x-p3.x)**2 + (p1.y -p3.y)**2)
    x = (a*a +b*b - c*c)/(2*a*b)
    return math.acos(x)

def press_keyboard(key,label, angle, threshold):
    title = str(get_active_window())
    if(title != "SpaceCadetPinball") and (title != "3D Pinball for Windows - Space Cadet"):
        for k in key:
                keyboard.release(k)
        return
    idx = 0
    if label == "Right":
        idx = 1
    print(math.degrees(angle))
    if threshold > math.degrees(angle):
            keyboard.release(key[idx])
    else:
        keyboard.press(key[idx])


# %%
with mp_hands.Hands(
    model_complexity=1,
    max_num_hands=2,
    # 손가락 감지 최소 신뢰성(1.0에 가까울수록 신뢰성이 높은 것만 인식)
    min_detection_confidence=0.7,
    # 손가락 추적 최소 신뢰성(1.0에 가까울수록 추적율이 높은 것만 인식)
    min_tracking_confidence=0.7
) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        # 사진을 좌/우 반전 시킨후 BGR에서 RGB로 변환
        # if sys.platform != 'win32':
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # else:
        #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        # 손 인식 결과
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        # 이미지를 다시 RGB에서 BGR로 변경
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                lbl = results.multi_handedness[idx].classification[0].label
                angle = get_angle(hand_landmarks.landmark[5], hand_landmarks.landmark[6], hand_landmarks.landmark[8])
                press_keyboard(['z', '/'],lbl, angle, 110.0)
                angle = get_angle(hand_landmarks.landmark[17], hand_landmarks.landmark[18], hand_landmarks.landmark[20])
                press_keyboard([' ', ' '],lbl, angle, 110.0)
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        # Flip the image horizontally for a selfie-view display.
        # if sys.platform != 'win32':
        cv2.imshow('MediaPipe Hands', image)
        # else:
            # cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            
        if cv2.waitKey(5) & 0xFF == 27:
            break
        
        


# %%
cap.release()
