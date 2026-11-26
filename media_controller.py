import pyautogui


class MediaController:

    def __init__(self):
        self.commands = {
            "PLAY_PAUSE": "playpause",
            "NEXT_TRACK": "nexttrack",
            "PREVIOUS_TRACK": "prevtrack",
            "VOLUME_UP": "volumeup",
            "VOLUME_DOWN": "volumedown",
            "MUTE": "volumemute"
        }

    def execute(self, command):

        if command not in self.commands:
            return False

        key = self.commands[command]

        pyautogui.press(key)

        return True