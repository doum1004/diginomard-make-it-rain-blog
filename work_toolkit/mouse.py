import time
import pyautogui

def click_mouse():
    pyautogui.click()

# add argument of sec (default 60)
def click_mouse_sec(pauseSec=60):
    try:
        i = 0
        while True:
            click_mouse()
            print("Mouse clicked! " + str(i) + " times.")
            i += 1                  
            time.sleep(pauseSec)  # Sleep for 1 minute
    except KeyboardInterrupt:
        print("\nScript terminated by user.")

# from main sys arg (default 60)
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        click_mouse_sec()
    else:
        click_mouse_sec(int(sys.argv[1]))

    