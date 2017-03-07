///////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2016, STEREOLABS.
//
// All rights reserved.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
///////////////////////////////////////////////////////////////////////////




/***************************************************************************************************
 ** This sample demonstrates how to grab images and depth/disparity map with the ZED SDK          **
 ** Both images and depth/disparity map are displayed with OpenCV                                 **
 ** Most of the functions of the ZED SDK are linked with a key press event (using OpenCV)         **
 ***************************************************************************************************/


#include <stdio.h>
#include <string.h>
#include <ctime>
#include <chrono>
#include <sys/time.h>
#include <stdlib.h>

#include <opencv2/opencv.hpp>

#include <zed/Camera.hpp>
#include <zed/utils/GlobalDefine.hpp>


#define MAX_FRAMES 1
#define MAX_DEPTH 20000
#define MAX_DIST 999999
#define BOUND_BOX_W 32
#define BOUND_BOX_H 32

//////////////////////////////////////////////  // intial vars
/////////////////////////////////////////// vars for bounding box
	int displaySize_W = 720;//720
	int displaySize_H = 404;//404

	int boundBox_cntx = displaySize_W/2;
 	int boundBox_cnty = displaySize_H/2;
	int boundBox_wdth = BOUND_BOX_W;
 	int boundBox_hght = BOUND_BOX_H;

	int boundBox_W_topL = boundBox_cntx - (boundBox_wdth/2);
 	int boundBox_H_topL = boundBox_cnty - (boundBox_hght/2);
	int boundBox_W_botR = boundBox_cntx + (boundBox_wdth/2) + 1;
 	int boundBox_H_botR = boundBox_cnty + (boundBox_hght/2) + 1;

	int temp_boundBox_W_topL = boundBox_W_topL;
 	int temp_boundBox_H_topL = boundBox_H_topL;
	int temp_boundBox_W_botR = boundBox_W_botR;
 	int temp_boundBox_H_botR = boundBox_H_botR;

	int trueArea = boundBox_wdth * boundBox_hght;
	int area = trueArea;

	int i;
	int j;

	int y_int;
	int x_int;

	float* ptr_image_num;
	float avgDist = 0.0;
	float frameDist = 0.0;
	float tempDist = 0.0;
	float shortestDist = MAX_DIST;

	float frames = 0;
	int framesValid = MAX_FRAMES;
///////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
typedef struct mouseOCVStruct {
    float* data;
    uint32_t step;
    cv::Size _image;
    cv::Size _resize;
    std::string name;
    std::string unit;
} mouseOCV;

mouseOCV mouseStruct;
mouseOCV* mydata = &mouseStruct;

////////////////////////////////////////////////////////////////////////////////////////////
static void onMouseCallback(int32_t event, int32_t x, int32_t y, int32_t flag, void * param) {
    if (event == CV_EVENT_LBUTTONDOWN) {//CV_EVENT_LBUTTONDOWN
        mouseOCVStruct* data = (mouseOCVStruct*) param;
	temp_boundBox_W_topL = x - (boundBox_wdth/2);
 	temp_boundBox_H_topL = y - (boundBox_hght/2);
	temp_boundBox_W_botR = x + (boundBox_wdth/2) + 1;
 	temp_boundBox_H_botR = y + (boundBox_hght/2) + 1;
    }
}

////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
int main(int argc, char **argv) {

    if (argc > 3) {
        std::cout << "Only the path of a SVO or a InitParams file can be passed in arg." << std::endl;
        return -1;
    }

    // Quick check input arguments
    bool readSVO = false;
    std::string SVOName;
    bool loadParams = false;
    std::string ParamsName;
    if (argc > 1) {
        std::string _arg;
        for (int i = 1; i < argc; i++) {
            _arg = argv[i];
            if (_arg.find(".svo") != std::string::npos) {
                // If a SVO is given we save its name
                readSVO = true;
                SVOName = _arg;
            }
            if (_arg.find(".ZEDinitParam") != std::string::npos) {
                // If a parameter file is given we save its name
                loadParams = true;
                ParamsName = _arg;
            }
        }
    }

    sl::zed::Camera* zed;

    if (!readSVO) // Live Mode
        zed = new sl::zed::Camera(sl::zed::HD720);
    else // SVO playback mode
        zed = new sl::zed::Camera(SVOName);

    // Define a struct of parameters for the initialization
    sl::zed::InitParams params;

    if (loadParams) // A parameters file was given in argument, we load it
        params.load(ParamsName);

    // Enables verbosity in the console
    params.verbose = true;


    sl::zed::ERRCODE err = zed->init(params);
    std::cout << "Error code : " << sl::zed::errcode2str(err) << std::endl;
    if (err != sl::zed::SUCCESS) {
        // Exit if an error occurred
        delete zed;
        return 1;
    }

    // Save the initialization parameters
    // The file can be used later in any zed based application
    params.save("MyParam");


    char key = ' ';
    int viewID = 0;
    int confidenceThres = 100;

    bool displayDisp = true;
    bool displayConfidenceMap = false;

    int width = zed->getImageSize().width;
    int height = zed->getImageSize().height;

    cv::Mat disp(height, width, CV_8UC4);
    cv::Mat anaglyph(height, width, CV_8UC4);
    cv::Mat confidencemap(height, width, CV_8UC4);

    cv::Size displaySize(displaySize_W, displaySize_H);
    cv::Mat dispDisplay(displaySize, CV_8UC4);
    cv::Mat anaglyphDisplay(displaySize, CV_8UC4);
    cv::Mat confidencemapDisplay(displaySize, CV_8UC4);

    sl::zed::SENSING_MODE dm_type = sl::zed::STANDARD;

    // Mouse callback initialization
    sl::zed::Mat depth;
    zed->grab(dm_type);
    depth = zed->retrieveMeasure(sl::zed::MEASURE::DEPTH); // Get the pointer
    // Set the structure
    mouseStruct._image = cv::Size(width, height);
    mouseStruct._resize = displaySize;
    mouseStruct.data = (float*) depth.data;
    mouseStruct.step = depth.step;
    mouseStruct.name = "DEPTH";
    mouseStruct.unit = unit2str(params.unit);

    // The depth is limited to 20 METERS, as defined in zed::init()
    zed->setDepthClampValue(MAX_DEPTH);//10000

    // Create OpenCV Windows
    // NOTE: You may encounter an issue with OpenGL support, to solve it either
    // 	use the default rendering by removing ' | cv::WINDOW_OPENGL' from the flags
    //	or recompile OpenCV with OpenGL support (you may also need the gtk OpenGL Extension
    //	on Linux, provided by the packages libgtkglext1 libgtkglext1-dev)
	int wnd_flag = cv::WINDOW_AUTOSIZE /*| cv::WINDOW_OPENGL*/;
	cv::namedWindow(mouseStruct.name, wnd_flag);
    cv::setMouseCallback(mouseStruct.name, onMouseCallback, (void*) &mouseStruct);
	cv::namedWindow("VIEW", wnd_flag);

    std::cout << "Press 'q' to exit" << std::endl;

    // Jetson only. Execute the calling thread on core 2
    sl::zed::Camera::sticktoCPUCore(2);

    sl::zed::ZED_SELF_CALIBRATION_STATUS old_self_calibration_status = sl::zed::SELF_CALIBRATION_NOT_CALLED;

//////////////////////////////////////////////  // Loop until 'q' is pressed
    while (key != 'q') {
        // Disparity Map filtering
        zed->setConfidenceThreshold(confidenceThres);

        // Get frames and launch the computation
        bool res = zed->grab(dm_type);

        if (!res) {
            if (old_self_calibration_status != zed->getSelfCalibrationStatus()) {
                std::cout << "Self Calibration Status : " << sl::zed::statuscode2str(zed->getSelfCalibrationStatus()) << std::endl;
                old_self_calibration_status = zed->getSelfCalibrationStatus();
            }

            depth = zed->retrieveMeasure(sl::zed::MEASURE::DEPTH); // Get the pointer

            // The following is the best way to retrieve a disparity map / image / confidence map in OpenCV Mat.
            // If the buffer is not duplicated, it will be replaced by a next retrieve (retrieveImage, normalizeMeasure, getView...)
            // Disparity, depth, confidence are 32F buffer by default and 8UC4 buffer in normalized format (displayable grayscale)


            // -- The next part is about displaying the data --

            // Normalize the disparity / depth map in order to use the full color range of gray level image
            if (displayDisp)
                slMat2cvMat(zed->normalizeMeasure(sl::zed::MEASURE::DISPARITY)).copyTo(disp);//normalizeMeasure
            else
                slMat2cvMat(zed->normalizeMeasure(sl::zed::MEASURE::DEPTH)).copyTo(disp);//normalizeMeasure


            // To get the depth at a given position, click on the disparity / depth map image
            cv::resize(disp, dispDisplay, displaySize);

////////////////////////////////////////////// show bounding box on depth display

			rectangle(dispDisplay, 
						cv::Point (boundBox_W_topL,boundBox_H_topL), 
						cv::Point (boundBox_W_botR,boundBox_H_botR), 
						cv::Scalar (0,0,255),
						3,
						8);

//////////////////////////////////////////////

            imshow(mouseStruct.name, dispDisplay);

            if (displayConfidenceMap) {
                slMat2cvMat(zed->normalizeMeasure(sl::zed::MEASURE::CONFIDENCE)).copyTo(confidencemap);
                cv::resize(confidencemap, confidencemapDisplay, displaySize);
                imshow("confidence", confidencemapDisplay);
            }

            // 'viewID' can be 'SIDE mode' or 'VIEW mode'
            if (viewID >= sl::zed::LEFT && viewID < sl::zed::LAST_SIDE)
                slMat2cvMat(zed->retrieveImage(static_cast<sl::zed::SIDE> (viewID))).copyTo(anaglyph);
            else
                slMat2cvMat(zed->getView(static_cast<sl::zed::VIEW_MODE> (viewID - (int) sl::zed::LAST_SIDE))).copyTo(anaglyph);

            cv::resize(anaglyph, anaglyphDisplay, displaySize);

////////////////////////////////////////////// show bounding box on regular display

			rectangle(anaglyphDisplay, 
						cv::Point (boundBox_W_topL,boundBox_H_topL), 
						cv::Point (boundBox_W_botR,boundBox_H_botR), 
						cv::Scalar (0,0,255),
						3,
						8);

//////////////////////////////////////////////

            imshow("VIEW", anaglyphDisplay);

/////////////////////////////////////////////// bounding box formula

			//atimer.start();

			boundBox_W_topL = temp_boundBox_W_topL;
		 	boundBox_H_topL = temp_boundBox_H_topL;
			boundBox_W_botR = temp_boundBox_W_botR;
		 	boundBox_H_botR = temp_boundBox_H_botR;

			// add up distances in each pixel of bounding box = sum(ith-distances)
			for (i = boundBox_H_topL; i < boundBox_H_topL + boundBox_hght; i++){
				y_int = (i * mydata->_image.height / mydata->_resize.height);
				ptr_image_num = (float*) ((int8_t*) mydata->data + y_int * mydata->step);

				for(j = boundBox_W_topL; j < boundBox_W_topL + boundBox_wdth; j++){
					x_int = (j * mydata->_image.width / mydata->_resize.width);		
					tempDist = ptr_image_num[x_int];
					if (isValidMeasure(tempDist)){
						if (frames == MAX_FRAMES-1.0 && tempDist < shortestDist);  //min dist at 24th frame
							shortestDist = tempDist;
						frameDist += tempDist;		
					}
					else
						area--;
					tempDist = -1.0;
				}
			}

			//sum(ith-distances) / area of valid distances
			frameDist /= ((float)area);

			if (isValidMeasure(frameDist)){
				avgDist += frameDist;	
			}
			else{
				framesValid--;
			}

			// if on the 24th frame, print average distance of average distances in 24 frames
			if(frames == MAX_FRAMES-1.0) {
				if (framesValid > 0){
					avgDist /= ((float)framesValid);
					if (isValidMeasure(avgDist)){
						printf("\nAvg Dist: %2.2f %s\n", avgDist, mydata->unit.c_str());
						printf("Min Dist: %2.2f %s\n", shortestDist, mydata->unit.c_str());
					}
					else {
						if (avgDist == TOO_FAR)
							printf("\nAvg Dist is too far.\n");
						else if (avgDist == TOO_CLOSE)
							printf("\nAvg Dist is too close.\n");
						else
							printf("\nAvg Dist not avaliable\n");
					}
				}

				shortestDist = MAX_DIST;
				framesValid = MAX_FRAMES;
				avgDist = 0.0;
				frames = 0;
		
				//dur = atimer.stop();
				//atimer.printTime(dur);
			}
			else
				frames++;

			frameDist = 0.0;
			area = trueArea;
///////////////////////////////////////////////////


            key = cv::waitKey(5);

            // Keyboard shortcuts
            switch (key) {
                case 'b':
                    if (confidenceThres >= 10)
                        confidenceThres -= 10;
                    break;
                case 'n':
                    if (confidenceThres <= 90)
                        confidenceThres += 10;
                    break;
                    // From 'SIDE' enum
                case '0': // Left
                    viewID = 0;
                    std::cout << "Current View switched to Left (rectified/aligned)" << std::endl;
                    break;
                case '1': // Right
                    viewID = 1;
                    std::cout << "Current View switched to Right (rectified/aligned)" << std::endl;
                    break;
                    // From 'VIEW' enum
                case '2': // Side by Side
                    viewID = 10;
                    std::cout << "Current View switched to Side by Side mode" << std::endl;
                    break;
                case '3': // Overlay
                    viewID = 11;
                    std::cout << "Current View switched to Overlay mode" << std::endl;
                    break;
                case '4': // Difference
                    viewID = 9;
                    std::cout << "Current View switched to Difference mode" << std::endl;
                    break;
                case '5': // Anaglyph
                    viewID = 8;
                    std::cout << "Current View switched to Anaglyph mode" << std::endl;
                    break;
                case 'c':
                    displayConfidenceMap = !displayConfidenceMap;
                    break;
                case 's':
                    dm_type = (dm_type == sl::zed::SENSING_MODE::STANDARD) ? sl::zed::SENSING_MODE::FILL : sl::zed::SENSING_MODE::STANDARD;
                    std::cout << "SENSING_MODE " << sensing_mode2str(dm_type) << std::endl;
                    break;
                case 'd':
                    displayDisp = !displayDisp;
                    break;
            }
        } else key = cv::waitKey(5);
    }

    delete zed;
    return 0;
}
