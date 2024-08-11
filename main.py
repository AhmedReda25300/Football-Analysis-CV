from utils import read_video,save_video
from trackers import Trackers
import cv2
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def main():
    # read video
    video_frames = read_video("Input_videos/08fd33_4.mp4")

    Tracker = Trackers("models/best.pt")
    tracks = Tracker.get_objects_tracks(video_frames,read_from_stub=True,stub_path="stubs/tracks_stubs.pkl")

    # save a cropped image for a player
    for track_id, player in tracks["players"][0].items():
        bbox = player["bbox"]
        print(bbox)
        frame = video_frames[0]
        cropped_image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
        #save cropped image
        cv2.imwrite(f"Output_videos/cropped_image.jpg", cropped_image)

        break


    # draw output video
    ##draw output tracks
    output_video_frames = Tracker.draw_annotations(video_frames,tracks)
    
    # save video
    save_video(output_video_frames, 'output_videos/output_video.avi')
if __name__ == "__main__":
    main()