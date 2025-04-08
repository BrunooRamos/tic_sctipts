from ultralytics import YOLO
import json
import cv2
from count_people import count_people

def main():
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Se cuenta el numero de personas en el frame, para esto se usa el modelo de YOLOv8n.
        frame_procesado, results = count_people(frame, model)
        cv2.imshow("YOLOv8 Person Detection", frame_procesado)

        #!Este results es el que se debe enviar a lambda. Antes debe guardar en redis.

        with open('detecciones.json', 'w') as f:
            json.dump(results, f, indent=4)
            

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()