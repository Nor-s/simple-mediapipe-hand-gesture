# simple-mediapipe-gesture

각도 계산으로 제스처를 인식하는 간단한 mediapipe 코드

## code

```python
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

lbl = results.multi_handedness[idx].classification[0].label
angle = get_angle(hand_landmarks.landmark[5], hand_landmarks.landmark[6], hand_landmarks.landmark[8])
press_keyboard(['z', '/'],lbl, angle, 110.0)
```

-   `get_active_window()`: 특정 프로세스를 지정할 수 있게 해주는 함수.
-   `get_angle()`: mediapipe의 handlandmark 좌표를 받아 각도를 계산해주는 함수
-   `press_keyboard()`: 임계치와 각도를 받아 특정 각도이상이면 키를 누르고, 이하면 키를 떼는 함수로 왼손, 오른손에 각각 하나씩 지정할 수 있다.

## example

-   z와 / 그리고 스페이스바를 인식하여 게임 플레이([SpaceCadetPinball](https://github.com/Nor-s/SpaceCadetPinball))

![hand](https://github.com/Nor-s/Nor-s.github.io/blob/main/img/Jan-19-2022%2022-50-44.gif?raw=true)
