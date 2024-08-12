import sys
sys.path.append('../')
from utils import get_center_of_bbox,measure_distance


class PlayerBallAssigner:
    def __init__(self):
        self.max_player_ball_dist=70

    def assign_ball_to_player(self,players,ball_bbox):
        ball_postion = get_center_of_bbox(ball_bbox)

        min_dis = 999999
        assigned_player=-1

        for player_id,player in players.items():
            player_bbox = player['bbox']

            dis_left = measure_distance((player_bbox[0],player_bbox[-1]),ball_postion)
            dis_right = measure_distance((player_bbox[2],player_bbox[-1]),ball_postion)
            distance = min(dis_left,dis_right)
            if  distance<self.max_player_ball_dist:
                min_dis = distance
                assigned_player = player_id

        return assigned_player

