from flask import Flask, request, jsonify
from ultralytics import YOLO
import base64
import os

def boxposition(tensor, screenwidth, screenheight):
    # Extract the coordinates from the tensor (x1, y1, x2, y2)
    x1, y1, x2, y2 = tensor  # Assuming tensor is a list of tensors, extract the first one

    # print(x1, y1, x2, y2)

    # Calculate the center of the bounding box
    box_center_x = (x1 + x2) / 2

    # The midline is at half of the screen width
    left_center_line = screenwidth / 3
    right_center_line = 2 * screenwidth / 3

    # Compare the center of the box with the midline
    if box_center_x > right_center_line:  # greater is on the left
        print("robot should turn right")  # robot needs to go right
        return "right"
    if box_center_x < left_center_line:
        print("robot should turn left")  # robot needs to go left
        return "left"
    if left_center_line <= box_center_x <= right_center_line:
        print("center")  # robot is in the center
        return "center"

#Initialize Flask app
app = Flask(__name__)

#Root route
@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Welcome to Flask!"})

#POST request
@app.route("/yolo_endpoint/", methods=["POST"])
def create_item():
    try:
        # Get the JSON data
        data = request.get_json()
        # Extract the base64 encoded image
        encodedimage = data.get("image")
        if not encodedimage:
            return jsonify({"error": "No image data provided"}), 400
        #Decode the image and save it to a file
        imagedata = base64.b64decode(encodedimage)
        uploaddir = "./uploads"
        tempimagepath = os.path.join(uploaddir, "temp_image.jpg")
        os.makedirs(uploaddir, exist_ok=True)

        with open(tempimagepath, "wb") as image_file:
            image_file.write(imagedata)

        model = YOLO('best.pt')  # Load model

        results = model(source=tempimagepath, show=False, conf=0.4, save=True, stream=True, imgsz=640)  # Inference

        for r in results:
            print(r.boxes.xyxy)
            if r.boxes.xyxy.shape[0] > 0:  # Check if there are any detections
                direction = boxposition(r.boxes.xyxy[0], 640, 480)
                return jsonify({"direction": direction})
            else:
                return jsonify({"message": "No detections found!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Run the Flask app
if __name__== "__main__":
    app.run(host='0.0.0.0', port=4000)
