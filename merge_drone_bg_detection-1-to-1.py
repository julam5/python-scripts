#!/usr/bin/env python

"""
Given N drone images and M background images, the script will output M x N x T images.
T indicates how many random (translation, scale, rotation) we apply to drone image.
Drone image MUST be PNG format (we need alpha channel).

Usage:
------
    python merge_drone_bg_detection.py [<path_to_drone_text_file>] [<path_to_background_text_file>]
    
Example:
------
    python merge_drone_bg_detection.py drone.txt bg.txt
"""
import cv2
import os
import numpy as np
#import scipy as sp
import matplotlib.pyplot as plt

from random import *
from scipy import ndimage as nd

import time

# ---------------------------------------------------------------- GLobal Vars
outputDir = "./merge_results_detection"

# ---------------------------------------------------------------- check if path is directory, if not exit program
def ifNotDirCreate(directoryName):
    if (os.path.isdir(directoryName) is False): 
        print ("> " + directoryName + " is not a valid directory! Creating it.")
        os.makedirs(directoryName)

# ---------------------------------------------------------------- Merging Drone BG Class
class MergingDroneBG(object):

    # ==============================================================================

    def __init__(self, drone_path, bg_path):

        self.drone_path = drone_path
        self.bg_path    = bg_path
        self.T          = 5
        #self.width      = 227
        #self.height     = 227
        self.bg_min_pix_len = 416
        self.num_drones_in_crop = 1
        
    # ==============================================================================

    def blend_transparent(self, face_img, overlay_t_img):
    
        # Split out the transparency mask from the colour info
        overlay_img = overlay_t_img[:,:,:3] # Grab the BRG planes
        overlay_mask = overlay_t_img[:,:,3:]  # And the alpha plane

        # Again calculate the inverse mask
        background_mask = 255 - overlay_mask

        # Turn the masks into three channel, so we can use them as weights
        overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
        background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

        # Create a masked out face image, and masked out overlay
        # We convert the images to floating point in range 0.0 -> 1.0
        face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
        overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

        # And finally just add them together, and rescale it back to an 8bit integer image
        return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))
        
    # ==============================================================================
        
    def preprocessDroneImg(self, drone_img):
        
        row, col    = drone_img.shape[:2]

        # rotation augmentation: -45 -> 45 degree
        rotation_matrix = cv2.getRotationMatrix2D((col/2, row/2), randint(0, 120) - 60, 1)
        new_img2 = cv2.warpAffine(drone_img, rotation_matrix, (col, row))

        # translation & scaling augmentation
        new_width = int(randint(20, 100))
        new_height = int(new_width * (int(randint(80, 120)) / 100.0))

        final_img = cv2.resize(new_img2, (new_width, new_height)) 

        return final_img
    # ==============================================================================
        
    def preprocessBgImg(self, bg_img):
        
        row, col    = bg_img.shape[:2]
        
        if row < self.bg_min_pix_len or col < self.bg_min_pix_len:
            if row < col:
                r = self.bg_min_pix_len / float(row)
                dim = (int(col * r), self.bg_min_pix_len)
                final_img = cv2.resize(bg_img, dim, interpolation = cv2.INTER_AREA)
            else:
                r = self.bg_min_pix_len / float(col)
                dim = (self.bg_min_pix_len, int(row * r))
                final_img = cv2.resize(bg_img, dim, interpolation = cv2.INTER_AREA)
            return final_img
        else:
            return bg_img
        
    # ==============================================================================

    def applyBlur(self, merged_img):

        chosen_to_blur = 16#randint(1,100)

        if chosen_to_blur <= 15:
            applied_blur = randint(0,1)
            if applied_blur == 0:
                chosen_sigma = randint(1,2)
                print "---Using gaussian_filter with sigma = %d" % chosen_sigma 
                merged_img[:,:,0] = nd.filters.gaussian_filter(merged_img[:,:,0] , sigma=chosen_sigma)
                merged_img[:,:,1] = nd.filters.gaussian_filter(merged_img[:,:,1] , sigma=chosen_sigma)
                merged_img[:,:,2] = nd.filters.gaussian_filter(merged_img[:,:,2] , sigma=chosen_sigma)
            else:
                chosen_size = randint(1,2)
                print "---Using median_filter with size = %d" % chosen_size 
                merged_img[:,:,0] = nd.filters.median_filter(merged_img[:,:,0] , size=chosen_size)
                merged_img[:,:,1] = nd.filters.median_filter(merged_img[:,:,1] , size=chosen_size)
                merged_img[:,:,2] = nd.filters.median_filter(merged_img[:,:,2] , size=chosen_size)
        else:
            print "---No blur applied"

        return merged_img

    # ==============================================================================

    def noisy(self,image):
        chosen_to_noise = randint(1,100)

        if chosen_to_noise <= 15:
            row,col,ch = image.shape
            s_vs_p = 0.5
            amount = 1 / 100.0

            print "---Adding salt and pepper with amount = %.2f" % amount 
            out = np.copy(image)

            # Salt mode
            num_salt = np.ceil(amount * image.size * s_vs_p)
            coords = [np.random.randint(0, i - 1, int(num_salt))
                  for i in image.shape]

            for index in range(0,len(coords[0])):
                out[coords[0][index],coords[1][index],0] = 255
                out[coords[0][index],coords[1][index],1] = 255
                out[coords[0][index],coords[1][index],2] = 255

            # Pepper mode
            num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
            coords = [np.random.randint(0, i - 1, int(num_pepper))
                  for i in image.shape]

            for index in range(0,len(coords[0])):
                out[coords[0][index],coords[1][index],0] = 0
                out[coords[0][index],coords[1][index],1] = 0
                out[coords[0][index],coords[1][index],2] = 0

            return out
        else:
            print "---No noise applied"
            return image

        #elif noise_typ =="speckle":
        #    noisy = image + 3 * image.std() * np.random.random(image.shape)
        #    return noisy 
        
    # ==============================================================================
        
    def merge(self):
    
        index = 0

        # loop for all drone images
        drones_files = open(self.drone_path, "r").readlines()
        bg_files     = open(self.bg_path, "r").readlines()
        
        ifNotDirCreate(outputDir)
        ifNotDirCreate(outputDir + "/images")
        ifNotDirCreate(outputDir + "/labels")

#        for drones_file in drones_files:
#            if '.png' in drones_file:
#                 drone preprocessing
#                drone_img  = cv2.imread(drones_file.rstrip(), cv2.IMREAD_UNCHANGED)
#                if drone_img is None:
#                    print "Bad drone image"
#                    continue

#                 loop for background images
#                for bg_file in bg_files:
#                    print '===============' 
#                    print '---Combine %s with %s' % (drones_file.rstrip() ,bg_file.rstrip())
#                    
#                     background preprocessing
#                    read_bg_img = cv2.imread(bg_file.rstrip())
#                    if read_bg_img is None:
#                        print "Bad bg image"
#                        continue
#                    
#                    bg_img = self.preprocessBgImg(read_bg_img)

        drone_names = []

        for found_drone in drones_files:
            if '.png' in found_drone:
                # drone preprocessing
                drone_names.append(found_drone)

        # loop for background images
        for bg_file in bg_files:
            print '===============' 

            # background preprocessing
            read_bg_img = cv2.imread(bg_file.rstrip())
            if read_bg_img is None:
                print "Bad bg image"
                continue

            bg_img = self.preprocessBgImg(read_bg_img)

            chosen_drone = randint(0,len(drone_names) - 1)
            
            drone_img  = cv2.imread(drone_names[chosen_drone].rstrip(), cv2.IMREAD_UNCHANGED)
            if drone_img is None:
                print "Bad drone image"
                continue

            print '---Combine %s with %s' % (drone_names[chosen_drone].rstrip() ,bg_file.rstrip())

            incr_width_crop = 0
            incr_height_crop = 0
            continue_crop = True
            while continue_crop:
                bg_img_roi = np.copy(bg_img[incr_height_crop:incr_height_crop + self.bg_min_pix_len, incr_width_crop:incr_width_crop + self.bg_min_pix_len])
                bg_img_roi_orig = np.copy(bg_img[incr_height_crop:incr_height_crop + self.bg_min_pix_len, incr_width_crop:incr_width_crop + self.bg_min_pix_len])                       

                bg_roi_row, bg_roi_col = bg_img_roi.shape[:2]
                

                # put drone on top of background
                for i in range(0,self.num_drones_in_crop):

                    # generate random drone orientation
                    drone_img_copy = np.copy(drone_img)
                    drone_img_new = self.preprocessDroneImg(drone_img_copy)
                    
                    rand_pos_x = int(randint(0, bg_roi_col - drone_img_new.shape[1]))
                    rand_pos_y = int(randint(0, bg_roi_row - drone_img_new.shape[0]))

                    roi_img = self.blend_transparent(bg_img_roi[rand_pos_y : rand_pos_y + drone_img_new.shape[0],rand_pos_x : rand_pos_x + drone_img_new.shape[1]], drone_img_new)
                    bg_img_roi[rand_pos_y : rand_pos_y + drone_img_new.shape[0],rand_pos_x : rand_pos_x + drone_img_new.shape[1]] = roi_img

                    # apply noise and blur to image
                    final_img = self.noisy(bg_img_roi)
                    final_img = self.applyBlur(final_img)

                    #cv2.rectangle(final_img, (rand_pos_x, rand_pos_y), (rand_pos_x + drone_img_new.shape[1], rand_pos_y + drone_img_new.shape[0]), (0,0,255),3)
                    
                    # record and save label for image
                    # format = "class id", "center point x coord", " center point y coord", "width", "height"
                    label_name = outputDir + "/labels/" + ('merge_%d.txt' % index)
                    print '---Saving label to %s' % label_name
                    savingFile = open(label_name, "wb")
                    label_class = 0 
                    label_cent_x = (rand_pos_x + (drone_img_new.shape[1])/2) / float(bg_roi_col)
                    label_cent_y = (rand_pos_y + (drone_img_new.shape[0])/2) / float(bg_roi_row)
                    label_width = (drone_img_new.shape[1]) / float(bg_roi_col)
                    label_height = (drone_img_new.shape[0]) / float(bg_roi_row)

                    label_line = str(label_class) + " " + str(label_cent_x) + " " + str(label_cent_y) + " " + str(label_width) + " " + str(label_height)
                    savingFile.write("%s\n" % label_line) 
                    savingFile.close()

                    # save image to directory
                    final_name = outputDir + "/images/" + ('merge_%d.jpg' % index)
                    print '---Saving to %s' % final_name
                    cv2.imwrite(final_name, final_img)
                    
                    # reset bg img and increment index
                    bg_img_roi = np.copy(bg_img_roi_orig)
                    index = index + 1

                # determine whether to move crop window or move to next bg image on list
                incr_width_crop += 300
                if incr_width_crop >= bg_img.shape[1] - self.bg_min_pix_len:
                    incr_width_crop = 0
                    incr_height_crop += 300
                    if incr_height_crop >= bg_img.shape[0] - self.bg_min_pix_len:
                        print "---Reached end of bg image, onto next one"
                        continue_crop = False
				
if __name__ == '__main__':
    import sys
    try:
        d_dir = sys.argv[1]
        b_dir = sys.argv[2]
    except:
        d_dir = '.'
        b_dir = '.'

    MergingDroneBG(d_dir, b_dir).merge()
    print '===============' 
