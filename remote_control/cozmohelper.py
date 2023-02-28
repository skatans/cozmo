import cozmo

_display_debug_annotations = False
DEBUG_ANNOTATIONS_DISABLED = False

class CozmoHelper:
    def __init__(self, coz):
        self.cozmo = coz
    
    def updateCozmo(self):
        if self.cozmo:
            self.cozmo.update()
            action_queue_text = ""
            i = 1
            for action in self.cozmo.action_queue:
                action_queue_text += str(i) + ": " + self.cozmo.action_to_text(action) + "<br>"
                i += 1

            return '''Action Queue:<br>''' + action_queue_text + '''
            '''
        return ""