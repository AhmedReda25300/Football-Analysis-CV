from utils import read_video,save_video
from trackers import Trackers
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
import cv2
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def main():
    # read video
    video_frames = read_video("Input_videos/08fd33_4.mp4")

    tracker = Trackers("models/best.pt")
    tracks = tracker.get_object_tracks(video_frames,read_from_stub=True,stub_path="stubs/tracks_stubs.pkl")

    # interplote ball position
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    # assign teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], 
                                    tracks['players'][0])


    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],   
                                                 track['bbox'],
                                                 player_id)
            
            tracks['players'][frame_num][player_id]['team'] = team 
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]


    # Assign ball Aquazation
    player_assigner = PlayerBallAssigner
    for frame_num , player_track in enumerate(track['players']):
        ball_bbox = track['ball'][frame_num][1]['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track,ball_bbox)

        if assigned_player != -1:
            track['players'][frame_num][assigned_player]['has_ball']=True

    # draw output video
    ##draw output  
    output_video_frames = tracker.draw_annotations(video_frames,tracks)   
    
    # save video
    save_video(output_video_frames, 'output_videos/output_video.avi')
if __name__ == "__main__":
    main()