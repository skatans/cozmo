import cozmo
import random
import time

# In this code, the traverse_maze function lets a user to control Cozmo to traverse a maze. 

# The prisoners_dilemma function prompts the human to decide whether they want to cooperate or betray (use explosives or not). 
# Cozmo always cooperates.

# The main function calls traverse_maze and prisoners_dilemma in sequence. 
# Finally, the cozmo.run_program function is used to start the program and connect to the robot.


# walk = False, use explosives = True
# TODO: starting amount?
# cozmo_explosives_left = 1
# human_explosives_left = 1

def traverse_maze(robot: cozmo.robot.Robot):
    # TODO: implement remote control
    # TODO: return when button pushed by the one controlling cozmo or something. True to keep going, False to quit programme.
    return  

def prisoners_dilemma(robot: cozmo.robot.Robot):
    # Interact with human
    
    robot.say_text("What do you want to do?").wait_for_completed()
    
    #TODO: HUMAN RESPONSE: event, tap object for explosion:
    # tap_object = wait_for(event_or_filter, timeout=30)  
    if (tap_object): 
        human_use_explo = True  
    else: human_use_explo = False 
    
    # COZMO CHOICE: 
    cozmo_use_explo = True
        
        
        
    # Cooperative states:
    
    if human_use_explo and cozmo_use_explo:
        print("Both players cooperate, they both use explosives.")
        robot.set_all_backpack_lights(cozmo.lights.green_light)
        # TODO: happy face anim
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabHappy, ignore_body_track=True).wait_for_completed() #happy face?
        time.sleep(2)
        robot.set_all_backpack_lights(cozmo.lights.off_light)
        
    elif human_use_explo and not cozmo_use_explo:
        print("Human cooperates, but the robot betrays. The human has to use explosives.")
        robot.set_all_backpack_lights(cozmo.lights.blue_light)
        # TODO: evil/satisfied/happy face anim
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabHappy, ignore_body_track=True).wait_for_completed() #happy face?
        time.sleep(2)
        robot.set_all_backpack_lights(cozmo.lights.off_light)
        
    elif not human_use_explo and cozmo_use_explo:
        print("Robot cooperates, but the human betrays. Cozmo has to use explosives.")
        robot.set_all_backpack_lights(cozmo.lights.red_light)
        # TODO: angry/sad face anim
        robot.play_anim_trigger(cozmo.anim.Triggers.CozmoSaysBadWord, ignore_body_track=True).wait_for_completed() #triggers angry face?
        time.sleep(2)
        robot.set_all_backpack_lights(cozmo.lights.off_light)
        
    else:
        print("Both players betray, walk the long way.")
        robot.set_center_backpack_lights(cozmo.lights.white_light)
        # TODO: neutral face anim
        robot.play_anim_trigger(cozmo.anim.Triggers.NeutralFace, ignore_body_track=True).wait_for_completed()
        time.sleep(2)
        robot.set_all_backpack_lights(cozmo.lights.off_light)


def main(robot: cozmo.robot.Robot):
    while (True):
        traverse_maze(robot)
        prisoners_dilemma(robot)


cozmo.run_program(main)