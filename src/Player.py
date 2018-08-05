# file: moveTest
#
# This file contains a script to intercept keybourd input and
# translate it to Malmo Commands
#
# ------------------------------------------------------------------------------
#
# imports
#
# ------------------------------------------------------------------------------

# malmo for interacting with Minecraft!
#
import MalmoPython as mp

# for data storage and manipulation
#
import pandas as pd
import json as js

# getting keyboard input
#
from _getch import _Getch

# I need more time
#
import time

# ------------------------------------------------------------------------------
#
# globals
#
# ------------------------------------------------------------------------------

# delimiters for observation strings
#
OBS_DELIM = ", "
TSTAMP_DELIM = ": "

# delay between commands from user
#
DELAY_TIME = 0.1

# moving
#
MOVE_FORWARD = "W"
MOVE_BACKWARD = "S"
STRAFE_LEFT = "A"
STRAFE_RIGHT = "D"
TURN_LEFT = "Q"
TURN_RIGHT = "E"
NO_ACTION = "X"

MOVE_INSTRUCTIONS = (
    "{:s}\n\t{:s}\n\t{:s}\n\t{:s}\n\t{:s}\n\t{:s}\n\t{:s}\n\t{:s}"
    .format("Commands:",
            "{:s} -> forward".format(MOVE_FORWARD),
            "{:s} -> Strafe left".format(MOVE_BACKWARD),
            "{:s} -> Strafe right".format(STRAFE_LEFT),
            "{:s} -> backward".format(STRAFE_RIGHT),
            "{:s} -> turn counterclockwise 90 degrees".format(TURN_LEFT),
            "{:s} -> turn clockwise 90 degrees".format(TURN_RIGHT),
            "{:s} -> No action".format(NO_ACTION)))

# ------------------------------------------------------------------------------
#
# class
#
# ------------------------------------------------------------------------------


class Player:

    # ----------------------------------
    #
    # constructor
    #
    # ----------------------------------

    def __init__(self, mission_file, action_delay=DELAY_TIME):

        # try to open the file
        #
        try:
            f = open(mission_file, "r")
        except IOError:
            print("Unable to open file {:s}".format(mission_file))
            raise

        # start the minecraft agent
        #
        self.mission = mp.MissionSpec(f.read(), True)
        self.agent = mp.AgentHost()

        # switch-like object for making decisions on movement
        #
        self.getAction = self.getAction()
        self.action_delay = action_delay

        # close the file
        #
        f.close()
    #
    # end of constructor

    # ----------------------------------
    #
    # methods
    #
    # ----------------------------------

    # method: start
    #
    # arguments: none
    #
    # return: none
    #
    # This method starts a Malmo mission
    #
    def start(self):

        # start the mission
        #
        record = mp.MissionRecordSpec()
        self.agent.startMission(self.mission, record)

        # wait for the mission to start
        #
        world_state = self.agent.getWorldState()

        # wait for mission to start
        # 
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            world_state = self.agent.getWorldState()
            for error in world_state.errors:
                print("Encountered Error: {:s}".format(error.text))
        #
        # end of while
    #
    # end of method

    # method: watch
    #
    # arguments: none
    #
    # return: list of observations
    #
    # This method watches a users input and records it
    #
    def watch(self):

        # variable to store observations
        #
        obs = []

        # get the world state and loop while the mission is going
        #
        world_state = self.agent.getWorldState()
        while world_state.is_mission_running:

            # get the observations
            #
            if world_state.observations:
                obs.append(str(world_state.observations[0]))
            world_state = self.agent.getWorldState()
        #
        # end of while

        # return observations
        #
        return obs
    #
    # end of function

    # method: listen_and_react_loop
    #
    # arguments:none
    #
    # return:
    #  actions: list of keyboard commands used
    #  states: list of world states
    #
    # listens to keyboard inputs and controls agent
    #
    def listen_and_react_loop(self):

        # lists for outputs
        #
        actions = []
        states = []

        # loop while the mission is running
        #
        world_state = self.agent.getWorldState()
        while world_state.is_mission_running:

            # get keyboard input and move
            #
            act = self.listen_and_react_once()

            # store world state and actions
            #
            states.append(world_state)
            actions.append(act)

            # get the world state
            #
            world_state = self.agent.getWorldState()
        #
        # end of while

        # return everything
        #
        return actions, states
    #
    # end of method

    # method: listen_and_react
    #
    # arguments:none
    #
    # return:
    #  actions: list of keyboard commands used
    #  states: list of world states
    #
    # listens to keyboard inputs and controls agent
    #
    def listen_and_react_once(self):

        # for getting input
        #
        getch = _Getch()

        # get keyboard input
        #
        print(MOVE_INSTRUCTIONS)
        user_input = str(getch()).upper()

        # branch on user input
        #
        if not self.react(user_input):
            print("{:s} is an invalid character")

        # wait a bit
        #
        time.sleep(self.action_delay)

        # return everything
        #
        return self.getAction(user_input)
    #
    # end of method

    # method: react
    #
    # argument: user input
    #
    # return: none
    #
    # sends user input to agent
    #
    def react(self, user_input):
        action = self.getAction(user_input)
        if action is None:
            return True
        elif action:
            self.agent.sendCommand(action)
            return True
        else:
            return False
    #
    # end of function

    # method: translate_pos_to_command
    #
    # arguments:
    #  obs_df: dataframe of observations to translate from positions
    #          to commands
    #  window: time window used to derive discrete commands from [default=0.5]
    #
    # return: commands to send to agent
    #
    # this method translates positions to discrete commands to be sent
    # to the agent
    # 
    def translate_pos_to_command(self, obs, window):

        #
        pass

    # ----------------------------------
    #
    # static methods
    #
    # ----------------------------------

    # ----------------------------------
    #
    # helper classes
    #
    # ----------------------------------

    class getAction:

        def __init__(self):

            self.switch = {
                MOVE_FORWARD: "move 1",
                MOVE_BACKWARD: "move -1",
                STRAFE_LEFT: "strafe -1",
                STRAFE_RIGHT: "strafe 1",
                TURN_LEFT: "turn -1",
                TURN_RIGHT: "turn 1",
                NO_ACTION: None
            }

        def __call__(self, user_input):
            if user_input in self.switch:
                return self.switch[user_input]
            else:
                return False

    #
    # end of helper class
#
# end of class

# ------------------------------------------------------------------------------
#
# functions
#
# ------------------------------------------------------------------------------

# function: obs_to_df
#
# arguments:
#  obs: iterable of observations to convert to dataframe
#
# return: dataframe of well structured observations
#
# converts a list observations to a dataframe
#
def obs_to_df(obs):

    # loop through the observations
    #
    pre_df = []
    times = []
    for ob in obs:

        # split the string by the delimiter
        #
        tstamp, data = ob.split(OBS_DELIM)

        # get the time of the string
        #
        tstamp = tstamp.split(TSTAMP_DELIM)[1]

        # convert the data from a json string to
        #
        data = js.loads(data)

        # add the time stamp to the times list
        #
        times.append(tstamp)

        # add the data to a list
        #
        pre_df.append(data)
    #
    # end of for

    # convert the list to a dataframe and return it
    #
    df = pd.DataFrame(pre_df)
    df = df.set_index(pd.to_datetime(times, format="%Y-%b-%d %H:%M:%S.%f"))
    return df
#
# end of function

