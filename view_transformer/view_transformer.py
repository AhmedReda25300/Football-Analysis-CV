import numpy as np
import cv2

class ViewTransformer:
    def __init__(self, input_shape, output_shape):
        court_width = 68
        court_length = 23.32 # 4 rectangles -->(((105/2)/9)*4)   105 is the length of the court

        self.pixcel_vertices = np.array([
            [110, 1035],
            [265,275],
            [910, 260],
            [1640, 915]
        ])

        self.target_vertices = np.array([
            [0, court_width],
            [0, 0],
            [court_length, 0],
            [court_length, court_width]
        ])


        self.pixcel_vertices = self.pixcel_vertices.astype(np.float32)
        self.target_vertices = self.target_vertices.astype(np.float32)

        self.prespective_transform = cv2.getPerspectiveTransform(self.pixcel_vertices, self.target_vertices)


    def transform_point(self, point):
        p = (int(point[0]), int(point[1]))
        is_inside = cv2.pointPolygonTest(self.pixcel_vertices, p, False)>0
        if not is_inside:
            return None
        reshaped_point = point.reshape(1, -1).astype(np.float32)
        transformed_point = cv2.perspectiveTransform(reshaped_point, self.prespective_transform)

        return transformed_point.reshape(-1,2)

    def add_transformed_postion_to_tracks(self, tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info['adjusted_position']
                    position = np.array(position)
                    position_transformed = self.transform_point(position)
                    if position_transformed is not None:
                        position_transformed = position_transformed.squeeze().tolist()
                    tracks[object][frame_num][track_id]['position_transformed'] = position_transformed

                    