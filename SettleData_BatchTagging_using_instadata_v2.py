import keras
import numpy as np
import os
import cv2

import csv
import pandas as pd
import pathlib
import fnmatch


import ssl

### Avoid certificat error (source: https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error)
import requests
requests.packages.urllib3.disable_warnings()

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


from keras.applications import inception_resnet_v2
from keras.preprocessing import image
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.imagenet_utils import decode_predictions
import matplotlib.pyplot as plt



from keras import applications
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.models import Sequential, Model
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras import backend as k
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
img_width, img_height = 331, 331
train_data_dir = "Photos_338_retraining/train"
validation_data_dir = "Photos_338_retraining/validation"
nb_train_samples = 81
nb_validation_samples = 36

batch_size = 16 # proportional to the training sample size..
epochs = 30

num_classes = 5




# or qt5.
# PyQt5 or similar required.. (https://stackoverflow.com/questions/52346254/importerror-failed-to-import-any-qt-binding-python-tensorflow)




default_path = '/Users/seo-b/Dropbox/KIT/FlickrEU/FlickrCNN'
os.chdir(default_path)
photo_path = default_path + '/Photos_50_Flickr'

### Read filenames
filenames = os.listdir(photo_path)

filenames1 = fnmatch.filter(filenames, "*.jpg")
filenames2 = fnmatch.filter(filenames, "*.JPG")

filenames = filenames1 + filenames2


img_width, img_height = 662, 662
train_data_dir = "Photos_168_retraining/train"
validation_data_dir = "Photos_168_retraining/validation"
nb_train_samples = 81
nb_validation_samples = 36

batch_size = 16 # proportional to the training sample size..

# Class #0 = backpacking
# Class #1 = hiking
# Class #2 = hotsprings
# Class #3 = noactivity
# Class #4 = otheractivities
classes = ["backpacking", "hiking", "hotsprings", "noactivity", "otheractivities"]

num_classes = len(classes)


##### Predict

from keras.models import model_from_json

# Model reconstruction from JSON file
with open('InceptionResnetV2_retrain_instagram_final_architecture.json', 'r') as f:
    model_trained = model_from_json(f.read())

# Load weights into the new model
model_trained.load_weights('TrainedWeights/InceptionResnetV2_retrain_instagram_epoch150_acc0.97.h5')

#Load the Inception_V3

# Load the base pre-trained model
# do not include the top fully-connected layer
# model = inception_v3.InceptionV3(include_top=False,  input_shape=(img_width, img_height, 3))
# Freeze the layers which you don't want to train. Here I am freezing the all layers.


# New dataset is small and similar to original dataset:
# There is a problem of over-fitting, if we try to train the entire network. Since the data is similar to the original data, we expect higher-level features in the ConvNet to be relevant to this dataset as well. Hence, the best idea might be to train a linear classifier on the CNN codes.
# So lets freeze all the layers and train only the classifier
#
# # first: train only the top layers (which were randomly initialized)
# # i.e. freeze all InceptionV3 layers
# for layer in model.layers[:]:
#     layer.trainable = False
# # Adding custom Layer
# x = model.output
# # add a global spatial average pooling layer
# x = GlobalAveragePooling2D()(x)
#
# # let's add a fully-connected layer
# x = Dense(1024, activation='relu')(x)
# # and a logistic layer -- let's say we have n classes
# predictions = Dense(num_classes, activation='softmax')(x)
#
#
# # creating the final model
# # this is the model we will train
# model_final = Model(inputs = model.input, outputs = predictions)
#
#
#
# model_final.load_weights('TrainedWeights/InceptionResnetV2_retrain_instagram_epoch150_acc0.97.h5')
#
modelname = "InceptionResnetV2"
dataname = "Photos_338"


# filename = 'photoid_19568808955.jpg' # granpa
filename = 'photoid_23663993529.jpg' # bridge





for filename in filenames:


    fname = photo_path + "/" + filename

    if os.path.isfile(fname):

        # load an image in PIL format
        # original = load_img(filename, target_size=(299, 299))
        original = load_img(fname, target_size=(662, 662))

        # convert the PIL image to a numpy array
        # IN PIL - image is in (width, height, channel)
        # In Numpy - image is in (height, width, channel)
        numpy_image = img_to_array(original)

        # Convert the image / images into batch format
        # expand_dims will add an extra dimension to the data at a particular axis
        # We want the input matrix to the network to be of the form (batchsize, height, width, channels)
        # Thus we add the extra dimension to the axis 0.
        image_batch = np.expand_dims(numpy_image, axis=0)


        # prepare the image (normalisation for channels)
        processed_image = inception_resnet_v2.preprocess_input(image_batch.copy())



        # get the predicted probabilities for each class
        predictions = model_trained.predict(processed_image)
        # print predictions
        dominant_feature_idx = np.argmax(predictions[0])

        # convert the probabilities to class labels
        predicted_class = classes[dominant_feature_idx]
        print('Predicted:', predicted_class )


        df = pd.DataFrame(predictions[0]).transpose()
        name_csv = default_path + "/Result/Tag_" + modelname + "/" + filename + ".csv"



        # df.to_csv(name_csv)
        header = classes
        df.columns = classes
        df.to_csv(name_csv, index=False, columns= header)



        # Heatmaap

        # `img` is a PIL image of size 224x224
        img = image.load_img(fname, target_size=(224, 224))

        # `x` is a float32 Numpy array of shape (224, 224, 3)
        x = image.img_to_array(img)

        # We add a dimension to transform our array into a "batch"
        # of size (1, 224, 224, 3)
        x = np.expand_dims(x, axis=0)

        # Finally we preprocess the batch
        # (this does channel-wise color normalization)
        x = vgg16.preprocess_input(x)

        preds = vgg_model.predict(x)
        print('Predicted:', decode_predictions(preds, top=10)[0])

        dominant_feature_idx = np.argmax(preds[0])


        # This is the dominant entry in the prediction vector
        dominant_output = vgg_model.output[:, dominant_feature_idx]

        # The is the output feature map of the `block5_conv3` layer,
        # the last convolutional layer in VGG16
        last_conv_layer = vgg_model.get_layer('block5_conv3')

        # This is the gradient of the "african elephant" class with regard to
        # the output feature map of `block5_conv3`
        grads = K.gradients(dominant_output, last_conv_layer.output)[0]

        # This is a vector of shape (512,), where each entry
        # is the mean intensity of the gradient over a specific feature map channel
        pooled_grads = K.mean(grads, axis=(0, 1, 2))

        # This function allows us to access the values of the quantities we just defined:
        # `pooled_grads` and the output feature map of `block5_conv3`,
        # given a sample image
        iterate = K.function([vgg_model.input], [pooled_grads, last_conv_layer.output[0]])

        # These are the values of these two quantities, as Numpy arrays,
        # given our sample image of two elephants
        pooled_grads_value, conv_layer_output_value = iterate([x])

        # We multiply each channel in the feature map array
        # by "how important this channel is" with regard to the elephant class
        for i in range(512):
            conv_layer_output_value[:, :, i] *= pooled_grads_value[i]

        # The channel-wise mean of the resulting feature map
        # is our heatmap of class activation
        heatmap = np.mean(conv_layer_output_value, axis=-1)


        # For visualization purpose, we will also normalize the heatmap between 0 and 1:

        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap)
        # plt.matshow(heatmap)
        # plt.show()


        # We use cv2 to load the original image
        img = cv2.imread(fname)

        # We resize the heatmap to have the same size as the original image
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))

        # We convert the heatmap to RGB
        heatmap = np.uint8(255 * heatmap)

        # We apply the heatmap to the original image
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # 0.4 here is a heatmap intensity factor
        superimposed_img = heatmap * 0.4 + img


        ## @todo vgg to incresv2
        # Save the image to disk
        cv2.imwrite("Result/Heatmap_" + modelname + "/AttentionMap_" + df[1][0] + "_" + filename, superimposed_img)



