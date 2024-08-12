import sys
sys.path.append('../')
from utils import measure_distance,get_foot_position
import numpy as np
import cv2

class SpeedAndDisEstimator:
    def __init__(self):
        self.frame_window = 5 # canlc the speed and distance every 5 frames
        self.frame_rate = 24


    def add_speed_and_dis_to_tracks(self,tracks):

        total_distance = {}

        for object,object_track in tracks.items():
            if object == 'ball' or object == 'referees':
                continue
            number_of_frames = len(object_track)
            for frame_num in range(0,number_of_frames,self.frame_window):
                last_frame = min(frame_num+self.frame_window,number_of_frames-1)

                for track_id,_ in object_track[frame_num].items():
                    if track_id not in object_track[last_frame]:
                        continue
                    start_postion = object_track[frame_num][track_id]["position_transformed"]
                    end_postion = object_track[last_frame][track_id]["position_transformed"]

                    if start_postion is None or end_postion is None:
                        continue
                    
                    dis_covered = measure_distance(start_postion,end_postion)
                    time_elpased = (last_frame-frame_num)/self.frame_rate

                    speed_m_per_s = dis_covered/time_elpased
                    speed_km_per_h = speed_m_per_s*3.6
                    
                    if object not in total_distance:
                        total_distance[object] = {}
                    
                    if track_id not in total_distance[object]:
                        total_distance[object][track_id] = 0

                    total_distance[object][track_id] += dis_covered

                    for frame_num_batch in range(frame_num,last_frame):
                        if track_id not in tracks[object][frame_num_batch]:
                            continue
                        tracks[object][frame_num_batch][track_id]["speed"] = speed_km_per_h
                        tracks[object][frame_num_batch][track_id]["distance"] = total_distance[object][track_id]
    
    def draw_speed_and_dis(self,video_frames, tracks):
        output_frames = []
        for frame_num, frame in enumerate(video_frames):
            for object, object_tracks in tracks.items():
                if object == 'ball' or object == 'referees':
                    continue
                for _, track_info in object_tracks[frame_num].items():
                    if 'speed' in track_info:
                        speed = track_info.get('speed',None)
                        distance = track_info.get('distance',None)
                        if speed is  None or distance is None:
                            continue
                        
                        bbox = track_info['bbox']
                        position = get_foot_position(bbox)
                        position = list(position)
                        position[1] +=40
                        position = tuple(map(int,position))
                        cv2.putText(frame,f"D: {distance:.2f} m",(position[0]-20,position[1]), cv2.FONT_HERSHEY_SIMPLEX,0.5,(32,32,32),2)
                        cv2.putText(frame,f"S: {speed:.2f} km/h",(position[0]-20,position[1]+20), cv2.FONT_HERSHEY_SIMPLEX,0.5,(32,32,32),2)

            output_frames.append(frame) 

        return output_frames
