import sys
import random
import time
import pyautogui

def move_mouse():
    # move mouse little around
    #rand x, y
    rangeVal = 3
    x = random.randint(-rangeVal, rangeVal)
    y = random.randint(-rangeVal, rangeVal)
    pyautogui.moveRel(x, y)

def click_mouse():
    pyautogui.click()

def press_ctrl_key_only():
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    
# add argument of sec
def mouse_keyboard(mouse, keyboard, pauseSec, endTimeMin):
    endTimeSec = endTimeMin * 60
    start_time = time.time()
    msg = ''
    if mouse:
        msg += 'Mouse clicked! '
    if keyboard:
        msg += 'Keyboard ctrl pressed! '
    
    try:
        i = 0
        checkTime = time.time()
        while True:
            # cal how many sec passed
            passingTime = time.time() - start_time

            # check checkTime is over pauseSec (sec), then do actions mouse and keyboard. And reset chec Time
            if time.time() - checkTime >= pauseSec:
                checkTime = time.time()
                if mouse:
                    click_mouse()
                    #move_mouse()
                if keyboard:
                    press_ctrl_key_only()

                i += 1
                # print format (ex, ## min ## sec. Mouse clicked! 1 times.) ## has to be two digits
                print(f'{int(passingTime / 60):02} min {int(passingTime % 60):02} sec. {msg}{i} times.')

            if endTimeSec != 0 and passingTime >= endTimeSec:
                print(f'End time reached {endTimeMin} mins. Exiting...')
                break

            #time.sleep(pauseSec)  # Sleep for 1 minute
    except KeyboardInterrupt:
        print("\nScript terminated by user.")

# from main sys arg (default 60)
if __name__ == '__main__':
    pauseSec = 120
    endTimeMin = 0 # mins
    if len(sys.argv) > 1:
        endTimeMin = int(sys.argv[1])
    mouse_keyboard(False, True, pauseSec, endTimeMin)

    