from ultralytics import YOLO

model = YOLO('models/best.pt')
results = model.predict('Input_videos/08fd33_4.mp4', save=True)
print(results[0])
print('______________________________________')
for box in results[0].boxes:
    print(box)