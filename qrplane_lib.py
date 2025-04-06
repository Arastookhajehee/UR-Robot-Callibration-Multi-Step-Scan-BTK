import pyrealsense2 as rs
import numpy as np
import cv2
import json
import os
import math

# a class called corner that has x, y, and d as its attributes
class Corner:
    def __init__ (self, x,y,d):
        self.x = x
        self.y = y
        self.d = d

# a class called corners that has corners TL, TB, TR, BR
# the constructor takes in the 4 corners as a list and stores them in the class
# the class has a function that returns the average depth of the corners
class QRPlane:

    plane_count = 100

    def __init__(self, corners, qr_content, standard_deviation = 1000, fixed = False, base_plane = ""):
        self.corners = corners
        self.qr_content = qr_content
        self.standard_deviation = standard_deviation
        self.solid = fixed
        self.base_plane = base_plane

    def to_string(self):
        return f"QRPlane: {self.qr_content}, {self.solid}, {self.base_plane}, {self.standard_deviation}" 
    
    @staticmethod
    def get_average_plane_list_with_standard_deviation(plane_list):
        # get the average plane
        average_plane = QRPlane.get_average_plane(plane_list)
        # get distance for each plane in the list
        distance_list = []
        for plane in plane_list:
            distance_list.append(QRPlane.get_distance_between_two_planes(average_plane, plane))
        # get the average plane distance
        average_distance = sum(distance_list) / len(distance_list)
        # get the standard deviation
        standard_deviation = 0
        for distance in distance_list:
            standard_deviation += (distance - average_distance)**2
        standard_deviation = math.sqrt(standard_deviation / len(distance_list))

        if (len(plane_list) >= QRPlane.plane_count):
            average_plane.standard_deviation = standard_deviation
        return average_plane

    @staticmethod
    def get_average_plane(planes):
        # corner averages
        corner1 = QRPlane.get_one_corner_average(planes, 0)
        corner2 = QRPlane.get_one_corner_average(planes, 1)
        corner3 = QRPlane.get_one_corner_average(planes, 2)
        corner4 = QRPlane.get_one_corner_average(planes, 3)
        return QRPlane([corner1, corner2, corner3, corner4], planes[0].qr_content)

    @staticmethod
    def get_distance_between_two_planes(plane1, plane2):
        corner1_distance = 0
        corner2_distance = 0
        corner3_distance = 0
        corner4_distance = 0
        for i in range(4):
            corner1_distance += QRPlane.get_distance_between_two_points(plane1.corners[i], plane2.corners[i])
            corner2_distance += QRPlane.get_distance_between_two_points(plane1.corners[i], plane2.corners[(i+1)%4])
            corner3_distance += QRPlane.get_distance_between_two_points(plane1.corners[i], plane2.corners[(i+2)%4])
            corner4_distance += QRPlane.get_distance_between_two_points(plane1.corners[i], plane2.corners[(i+3)%4])
        c1_average = corner1_distance / 4
        c2_average = corner2_distance / 4
        c3_average = corner3_distance / 4
        c4_average = corner4_distance / 4
        return (c1_average + c2_average + c3_average + c4_average) / 4

    @staticmethod
    def get_distance_between_two_points(corner1, corner2):
        return math.sqrt((corner1.x - corner2.x)**2 + (corner1.y - corner2.y)**2 + (corner1.d - corner2.d)**2)
    

    @staticmethod
    def get_one_corner_average(corners_list,index):
        # get the average x, y, and d of the corners
        average_x = 0
        average_y = 0
        average_d = 0

        for corners in corners_list:
            corner = corners.corners[index]
            average_x += corner.x
            average_y += corner.y
            average_d += corner.d
        average_x = average_x / len(corners_list)
        average_y = average_y / len(corners_list)
        average_d = average_d / len(corners_list)
        return Corner(average_x, average_y, average_d)
        
    def serialize(self):
        return json.dumps(self, default=QRPlane.serialize_complex_obj)
    
    # a function that writes the corners to a file if the corners are valid
    @staticmethod
    def write_corners_to_file(content, path):
        with open(path, "w") as file:
            file.write(content)

    @staticmethod
    def serialize_complex_obj(obj):
        if isinstance(obj, Corner) or isinstance(obj, QRPlane):
            return obj.__dict__
        if isinstance(obj, np.generic):
            return obj.item()  
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


class D435_Scanner:

    def __init__(self):
        # Configure depth and color streams
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        # Start the pipeline
        pipeline.start(config)
        self.pipeline = pipeline

    def get_frames_and_coordinates(self):
            pipeline = self.pipeline
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                return None, None, None

            # Create alignment primitive with color as its target stream:
            align = rs.align(rs.stream.color)
            frames = align.process(frames)
            # Update color and depth frames:
            aligned_depth_frame = frames.get_depth_frame()

            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                return None, None, None

            depth_intrinsics = rs.video_stream_profile(aligned_depth_frame.profile).get_intrinsics()
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Generate point cloud
            pc = rs.pointcloud()
            pc.map_to(color_frame)
            points = pc.calculate(aligned_depth_frame)
            vtx = np.asanyarray(points.get_vertices())
            tex = np.asanyarray(points.get_texture_coordinates())

            # Extracting x, y, z coordinates
            coords = np.ndarray(buffer=vtx, dtype=np.float32, shape=(480, 640, 3))  # adjust the shape according to the frame resolution

            return color_image, coords

    @staticmethod
    def get_corner_coordinates(decoded_objects, coords,all_planes,color_image):
                corner_objects = []
                for obj in decoded_objects:
                    points = obj.polygon
                    for point in points:
                        x = point[0]
                        y = point[1]
                        xCoord = round(coords[y][x][0] * 1000, 3)
                        yCoord = round(coords[y][x][1] * 1000, 3)
                        dCoord = round(coords[y][x][2] * 1000, 3) 
                        corner = Corner(-xCoord, -yCoord, dCoord)
                        corner_objects.append(corner)
                    for point in points:
                        cv2.circle(color_image, tuple(point), 5, (255, 0, 0), -1)
                        cv2.putText(color_image, f"{x}, {480 - y}, {dCoord}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        # display the content of the qr code
                        cv2.putText(color_image, obj.data.decode("utf-8"), (x +15, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    
                    if len(corner_objects) == 4:
                        # print( str(obj.data))
                        # extract the text from the obj.data
                        utf_str = obj.data.decode("utf-8")
                        corners_obj = QRPlane(corner_objects, utf_str)
                        # add the corners object to the all_planes dictionary
                        # if the qr content is not in the dictionary, add a list for planes with the qr content
                        # else append the corners object to the list of the qr content
                        if utf_str not in all_planes:
                            all_planes[utf_str] = []
                        all_planes[utf_str].append(corners_obj)
                        # if there is more than 30 planes in each qr content list, remove the first element
                        for key in all_planes:
                            if len(all_planes[key]) > QRPlane.plane_count:
                                all_planes[key].pop(0)
                return color_image
    
    @staticmethod
    def process_planes(all_planes):
            try:
                average_planes = {}
                for key in all_planes:
                    average_corners = QRPlane.get_average_plane_list_with_standard_deviation(all_planes[key])
                    average_planes[key] = average_corners
                    
                return average_planes
            except Exception as e:
                return None
            

# create a list of planes
all_planes = {}
corners_list = {}
scanner = D435_Scanner()


