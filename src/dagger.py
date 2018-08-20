# -----------------------------------------------------------------------------
#
# program: Dagger Simulation
#
# description: simulates the dagger algorithm using minecraft to teach the
#              actor to stay on course
#
# -----------------------------------------------------------------------------
#
# imports
#
# -----------------------------------------------------------------------------

# to control Minecraft
#
from Player import Player

# data modules
#
from PIL import Image
import numpy as np

# import imageio
from matplotlib import pyplot as plt

# modules for deep learning
#
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.optimizers import Adam


# -----------------------------------------------------------------------------
#
# globals
#
# -----------------------------------------------------------------------------

# size of action vector
#
ACTION_DIM = 1

# image dimensions
#
IMG_DIM = (64, 64, 3)

# number of dagger iterations
#
DAGGER_ITER = 5

# batch size and number of epochs
#
BATCH_SIZE = 32
NB_EPOCH = 100

# size to resize images
#
NEW_IMAGE_SIZE = (64, 64)

# mission xml file and delay time between actions
#
MISSION_FILE = "../config/mission.xml"
DELAY_TIME = 0.1


# -----------------------------------------------------------------------------
#
# functions
#
# -----------------------------------------------------------------------------


# function: img_reshape
#
# arguments:
#  input_img: image from simulation to convert to standard image array format
#
# return: three dimensional array of image
#
# converts image from simulation to format recognizable my PIL
#
def img_reshape(input_img):

    # reshape the image
    #
    _img = np.transpose(input_img, (1, 2, 0))
    _img = np.flipud(_img)
    _img = np.reshape(_img, (1, *input_img.shape))

    # exit gracefully
    #
    return _img
#
# end of function


# function: img_prepare
#
# arguments:
#  img: image to be prepared to be written to gif
#
# return: three dimensional array of resized image
#
# resizes an image to prepare it to be written to a gif
#
def img_prepare(img):

    # reshape and resize the image
    #
    im = Image.fromarray(img)
    im = im.resize(NEW_IMAGE_SIZE, Image.ANTIALIAS)

    # exit gracefully
    #
    return np.array(im).reshape((1, *IMG_DIM))
#
# end of function

# -----------------------------------------------------------------------------
#
# main
#
# -----------------------------------------------------------------------------


def main():

    # ---------------------------------
    #
    # initial run
    #
    # ---------------------------------

    # object to interact with Minecraft
    #
    player = Player(MISSION_FILE, action_delay=DELAY_TIME)

    # start a mission and listen
    #
    player.start()
    actions, states = player.listen_and_react_loop(limit_to=["Q", "E", "X"],
                                                   move_forward=True)

    # ---------------------------------
    #
    # create neural network
    #
    # ---------------------------------

    # credit for model design:
    # https://github.com/fchollet/keras/blob/master/examples/cifar10_cnn.py
    #
    print("constructing neural net!!")
    model = Sequential()

    model.add(Convolution2D(32, 3, 3, border_mode='same',
                            input_shape=IMG_DIM,
                            kernel_initializer="normal"))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3, kernel_initializer="normal"))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(64, 3, 3, border_mode='same',
                            kernel_initializer="normal"))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, kernel_initializer="normal"))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512, kernel_initializer="normal"))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(ACTION_DIM, kernel_initializer="normal"))
    model.add(Activation('tanh'))

    model.compile(loss='mean_squared_error',
                  optimizer=Adam(lr=1e-3),
                  metrics=['mean_squared_error'])

    # prepare images
    #
    print("dagger:: preparing images!!")
    frames = np.zeros((0, *IMG_DIM))
    for state in states:
        frame = np.array(state.video_frames[-1].pixels).reshape((360, 480, 3))
        frames = np.concatenate((frames, img_prepare(frame)), axis=0)

    # prepare actions
    #
    acts = []
    act_map = {None: 0, "turn -1": -1, "turn 1": 1}
    for act in actions:
        acts.append(act_map[act])

    # train model
    #
    model.fit(frames, acts, batch_size=BATCH_SIZE,
              epochs=NB_EPOCH, shuffle=True)

    # ---------------------------------
    #
    # iteratively train model
    #
    # ---------------------------------

    # aggregate and retrain for multiple dagger iterations
    #
    for itr in range(DAGGER_ITER):
        continue
    #
    # end of for
#
# end of main


# begin gracefully
#
if __name__ == "__main__":
    main()
#
# end of program
