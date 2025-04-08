import cv2
from datetime import datetime

def count_people(frame, model):
    results = model(frame, verbose=False)
    personas_detectadas = 0
    detecciones = []
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0])

            if cls == 0:  
                personas_detectadas += 1
                deteccion = {
                    "id": personas_detectadas,
                    "confianza": round(conf, 2),
                    "coordenadas": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    }
                }
                detecciones.append(deteccion)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Person {conf:.2f}", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_personas": personas_detectadas,
        "detecciones": detecciones
    }
    
    return frame, results