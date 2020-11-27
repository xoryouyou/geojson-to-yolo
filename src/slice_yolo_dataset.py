import cv2
import random
import glob
import tqdm
import os.path

def fetch_annotations(annotation_file, image_width, image_height):
    # open annotation file and get bboxes
    f = open(annotation_file, "r")
    annotations = f.read().splitlines()

    bboxes = []
    labels = []

    for a in annotations:
        # split by space
        values = a.split(" ")
        # store class in labels
        labels.append(values[0])
        # map values to float and skip first class value
        # center_x center_y image_width image_height
        values = list(map(lambda x: float(x), values[1:]))

        # scale to full image resolution

        half_width = values[2] / 2
        half_height = values[3] / 2
        
        # force to int
        scaled_bbox = [
            int((values[0] - half_width) * image_width),
            int((values[1] - half_height) * image_height),
            int((values[0] + half_width) * image_width),
            int((values[1] + half_height) * image_height)
        ]
        
        bboxes.append(scaled_bbox)

    return (bboxes, labels, annotations)


def plot_annotations(image_file, annotation_file):

    # read image and properties
    img = cv2.imread(image_file)
    image_height, image_width, channels = img.shape

    bboxes, labels, annotations = fetch_annotations(
        annotation_file, image_width, image_height)

    for idx, bbox in enumerate(bboxes):
        topleft = (bbox[0], bbox[1])
        bottomright = (bbox[2], bbox[3])
        print(topleft, bottomright)
        img = cv2.rectangle(img, topleft, bottomright, 0xFF0000, 2)

    print("image_width: ", image_width, " image_height: ", image_height)
    img = cv2.resize(img, (1024,1024))
    cv2.imshow("Image", img)


def slice_image(image_file, annotation_file, slice_height=256, slice_width=256, output_path="./test/slices",debug=False):
    overlap = 0.15
    zero_frac_thresh = 0.1
    win_size = slice_width * slice_height
    img = cv2.imread(image_file)
    image_height, image_width, channels = img.shape


    pad = 0
    # if slice sizes are large than image, pad the edges
    if slice_height > image_height:
        pad = slice_height - image_height
    if slice_width > image_width:
        pad = max(pad, slice_width - image_width)
    # pad the edge of the image with black pixels
    if pad > 0:
        border_color = (0, 0, 0)
        img = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=border_color)
        image_height, image_width, channels = img.shape

    bboxes, labels, annotations = fetch_annotations(annotation_file, image_width, image_height)
     
    if debug:
        print("BBOX:",bboxes[0] , " anno ", annotations[0])
        for bbox in bboxes:

            img = cv2.rectangle(
                    img, 
                    # (slice_bbox[0]+ bbox[0], slice_bbox[1] + bbox[1]), 
                    # (slice_bbox[0]+ bbox[2], slice_bbox[1] + bbox[3]), 
                    (bbox[0], bbox[1]), 
                    (bbox[2], bbox[3]), 
                    (255,127,127), 2)

        cv2.imshow("Image", img)





    slice_count = 0
    dx = int((1. - overlap) * slice_width)
    dy = int((1. - overlap) * slice_height)
    for y in range(0, image_height, dy):  # sliceHeight):
        for x in range(0, image_width, dx):  # sliceWidth):
            slice_count += 1

            if y + slice_height > image_height:
                y0 = image_height - slice_height
            else:
                y0 = y
            if x + slice_width > image_width:
                x0 = image_width - slice_width
            else:
                x0 = x


            # get the color image
            window_color = img[y0:y0 + slice_height, x0:x0 + slice_width]
            # get black and white image
            window = cv2.cvtColor(window_color, cv2.COLOR_BGR2GRAY)

            # calculate threshold (slice might be on border and be padded black)
            ret, thresh1 = cv2.threshold(window, 2, 255, cv2.THRESH_BINARY)
            # count color pixels
            non_zero_counts = cv2.countNonZero(thresh1)
            # calculate black pixels
            zero_counts = win_size - non_zero_counts
            # calc fracture
            zero_frac = float(zero_counts) / win_size
            # skip if image is mostly empty -> fracture to high
            if zero_frac >= zero_frac_thresh:
                # print("Zero frac too high at:", zero_frac)
                continue

            # slice bounding box
            slice_bbox = [x0, y0, x0+slice_width, y0+slice_height]
            
            # check which annotations are completely contained in slice
            atleast_one_bbox = False
            slice_annotations = []

            bboxes_in_slice = []
            labels_in_slice = []

            for bbox_idx, bbox in enumerate(bboxes):
                is_in = a_fully_in_b(bbox, slice_bbox)

                if is_in:
                    atleast_one_bbox = True
                    slice_annotations.append(annotations[bbox_idx])
                    bboxes_in_slice.append( [
                        bbox[0] - slice_bbox[0], 
                        bbox[1] - slice_bbox[1],
                        bbox[2] - slice_bbox[0], 
                        bbox[3] - slice_bbox[1] ]
                    )
                    labels_in_slice.append(labels[bbox_idx])

                    if debug:
                        window = cv2.rectangle(
                            window, 
                            # (slice_bbox[0]+ bbox[0], slice_bbox[1] + bbox[1]), 
                            # (slice_bbox[0]+ bbox[2], slice_bbox[1] + bbox[3]), 
                            (bbox[0] - slice_bbox[0], bbox[1] - slice_bbox[1]), 
                            (bbox[2] - slice_bbox[0], bbox[3] - slice_bbox[1]), 
                            (255,255,255), 2)

            if atleast_one_bbox:
                
              
             

                slice_annotation_file_name = output_path+"labels/"+image_file.split("/")[-1][:-4]+"_{:04d}".format(slice_count)+".txt"
                slice_image_file_name = output_path+"images/"+image_file.split("/")[-1][:-4]+"_{:04d}".format(slice_count)+".png"
                if debug:
                    print("Found: ",len(slice_annotations), " annotations in slice")
                    print("Slice Image {:04d}:  {}".format(slice_count,slice_image_file_name))
            
                # print("filename:", slice_annotation_file_name)
                slice_annotation_file = open(slice_annotation_file_name, "w")
                for i, b in enumerate(bboxes_in_slice):
                
                    top_x = b[0]
                    top_y = b[1]

                    bottom_x = b[2]
                    bottom_y = b[3]

                    # print("@)@)@)@)@ ",top_x, top_y,bottom_x,bottom_y)

                    center_x = (bottom_x + top_x) / 2
                    center_y = (bottom_y + top_y) / 2

                    area_x = bottom_x - top_x
                    area_y = bottom_y - top_y

                    line = "{} {} {} {} {}".format(labels_in_slice[i], center_x / slice_width, center_y / slice_height, area_x / slice_width, area_y / slice_height)
                    if debug:
                        print("\t BBox in slice:"+line)
                    slice_annotation_file.write(line + "\n")
                    
                    
                if debug:
                    print("\tWriting to:" + slice_annotation_file_name)
                slice_annotation_file.close()
                
                cv2.imwrite(slice_image_file_name, window_color)

            


                # only for debug show the found slices with boxes
                if debug:
                    cv2.imshow("slice-"+str(slice_count), window)


def a_fully_in_b(a,b):
    if a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]:
        return True
    else:
        return False



def plot_bboxes(image_file, bboxes,names):
    # # to test
    # a = [75,75,100,100]
    # b = [50,50,150,150]
    # c = [25,25,200,200]
    # d = [10,10,50,50]
    # names = ["a","b","c","d"]

    # bboxes = [a,b,c,d]

    # for idx, x in enumerate(bboxes):
    #     for idy, y in enumerate(bboxes):
    #         if idx == idy:
    #             continue
    #         print( names[idx], " ", names[idy], " ",a_fully_in_b(x,y))

    # plot_bboxes(image_file, bboxes, names )
    # img = cv2.imread(image_file)
    # image_height, image_width, channels = img.shape

    for idx, bbox in enumerate(bboxes):
        # plot rectangle
        img = cv2.rectangle(img, (bbox[0],bbox[1]), (bbox[2],bbox[3]), (random.randint(1,255),random.randint(1,255),random.randint(1,255)), 2)
        # add text
        img = cv2.putText(img, names[idx], (bbox[0], bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)


    cv2.imshow("Image", img)


if __name__ == "__main__":

    # TODO: argparse, create&check out folders,  multiprocessin pool
    
    # SLICE
    # images = glob.glob("/run/media/xoryouyou/Data/datasets/berlin_ORTHO_2019/images/*.png")    

    # for idx, image in enumerate(tqdm.tqdm(images)):
    #     annotation_file = image.replace("images","tree_labels").replace(".png",".txt")
        
    #     if not os.path.isfile(annotation_file):
    #         print(" NO annotation for ",image)
    #         continue
        
    #     slice_image(image, annotation_file,output_path="./out/slices/")

    # images = glob.glob("../datasets/dota/validation/images/*.png")    

    # for idx, image in enumerate(tqdm.tqdm(images)):
        
    #     annotation_file = image.replace("images","labels").replace(".png",".txt")
    #     slice_image(image, annotation_file,output_path="./test/validation_slices/")




    # # TESTING

    # image_file = "../datasets/cowc/yolo/images/slice_Utah_AGRC_12TVL160640-CROP_1728_6528_256_256_0.png"
    # annotation_file = "../datasets/cowc/yolo/labels/slice_Utah_AGRC_12TVL160640-CROP_1728_6528_256_256_0.txt"
    
    # slice_image(image_file, annotation_file,output_path="./test/training_slices/",debug=True)

    # # original
    # image_file = "../Data/datasets/berlin_ORTHO_2019/images/dop20rgb_370_5806_2_be_2019.png"
    # annotation_file = "../Data/datasets/berlin_ORTHO_2019/labels/dop20rgb_370_5806_2_be_2019.txt"

    # # # annotate
    image_file = "./out/car_slices/images/dop20rgb_392_5818_2_be_2019_0086.png"
    annotation_file = "./out/car_slices/labels/dop20rgb_392_5818_2_be_2019_0086.txt"
    
    plot_annotations(image_file, annotation_file)

    # # wait and show image
    # # break if images was closed by window manager or ESC was hit
    while True:
        keyCode = cv2.waitKey(1)

        if keyCode == 27:
            break
        if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
            break

    # cleanup
    cv2.destroyAllWindows()
