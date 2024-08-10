from ultralytics import YOLO
import supervision as sv
import pickle
import os
import cv2
import numpy as np
import sys
sys.path.append("../")
from utils import get_center_of_bbox, get_bbox_width
class Trackers:

    def __init__(self,model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()

    def detect_frames(self,frames):
        detections = []
        batch_size = 16#--> 16 frames per batch
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size],conf=0.1)
            detections+=detections_batch
            
        return detections   


 
    def get_objects_tracks(self,frame,read_from_stub=False,stub_path=None):


        if read_from_stub is True and stub_path is not None and os.path.exists(stub_path): 
            with open(stub_path, 'rb') as f:
                tracks = pickle.load(f)
            return tracks
        

        detections = self.detect_frames(frame)

        tracks={
            "players":[],
            "ball":[],
            "referees":[]
        }

        for frame_num, detection in enumerate(detections):
            cls_name = detection.names#-->{0:person, 1:ball, 2:goal}
            cls_name_inv ={v:k for k,v in cls_name.items()} #-->{person:0, ball:1, goal:2}
            
            # convert to supervision format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # convert goalkeeper to player object
            for object_index,class_id in enumerate(detection_supervision.class_id):
                if cls_name[class_id] == 'goalkeeper':
                    detection_supervision.class_id[object_index] = cls_name_inv['player']

            #Track the objects
            detections_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detections_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_name_inv['player']:
                    tracks["players"][frame_num][track_id] = {"bbox":bbox}
                elif cls_id == cls_name_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox":bbox}


            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_name_inv['ball']:
                    tracks["ball"][frame_num][1] = {"bbox":bbox}#--> 1 is the id of the ball

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(tracks, f)

        return tracks
        ''''
        --> {
            players:[
            {0:{"bbox":[1,2,3,4]},1:{"bbox":[1,2,3,4]},12:{"bbox":[1,2,3,4]}}, #--> frame number 0
            {0:{"bbox":[1,2,3,4]},1:{"bbox":[1,2,3,4]},11:{"bbox":[1,2,3,4]}}, #--> frame number 1
            ......
            ],

            ball:[
            {1:{"bbox":[1,2,3,4]}}, #--> frame number 0
            {1:{"bbox":[1,2,3,4]}}, #--> frame number 1
            ......
            ],
            referees:[
            {0:{"bbox":[1,2,3,4]},1:{"bbox":[1,2,3,4]},12:{"bbox":[1,2,3,4]}}, #--> frame number 0
            {0:{"bbox":[1,2,3,4]},1:{"bbox":[1,2,3,4]},11:{"bbox":[1,2,3,4]}}, #--> frame number 1
            ......
            ]
            }'''
        

    def draw_ellipse(self,frame,bbox,color,track_id=None):
        y2 = int(bbox[3])
        x_center,_ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)    

        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=(int(width),int(0.35*width)),
            angle=0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
            )
        
        rectangle_width = 40
        rectangle_height=20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2- rectangle_height//2) +15
        y2_rect = (y2+ rectangle_height//2) +15

        if track_id is not None:
            cv2.rectangle(frame,
                          (int(x1_rect),int(y1_rect) ),
                          (int(x2_rect),int(y2_rect)),
                          color,
                          cv2.FILLED)
            
            x1_text = x1_rect+12
            if track_id > 99:
                x1_text -=10
            
            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text),int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )

        return frame



    def draw_traingle(self,frame,bbox,color):
        y= int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)



    def draw_annotations(self,video_frame,tracks):

        output_video_frames = []
        for frame_num, frame in enumerate(video_frame):
            output_frame = frame.copy()
            
            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referees_dict = tracks["referees"][frame_num]

            # Draw players
            for track_id, player in player_dict.items():
                frame = self.draw_ellipse(frame,player["bbox"],(0, 255, 0),track_id)
            
            output_video_frames.append(frame)
            # Draw ball 
            for track_id, ball in ball_dict.items():
                frame = self.draw_traingle(frame, ball["bbox"],(0,255,0))
                
            # Draw referees
            for track_id, referee in referees_dict.items():
                frame = self.draw_ellipse(frame,referee["bbox"],(0, 255, 255))

        return output_video_frames