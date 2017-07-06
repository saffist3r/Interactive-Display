from flask import Flask
from flask import jsonify
from main_program import get_depth_object,screen_calibration
from contour_optmisation import center_detect
app = Flask(__name__)
#GET the depth of the pixels where there is an object detected
@app.route('/depth')
def depthFunction():
    return jsonify(get_depth_object())

#Get the center of the detected object from RGB Camera
@app.route('/center')
def centerFunction():
    return jsonify(center_detect())

#Get the screen resolution for later maping
@app.route('/edges')
def contourFunction():
    return jsonify(screen_calibration())
def calibrationFunction():
    return "Calibration"
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, use_reloader=False)