import json

from flask import Blueprint, render_template, jsonify

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis')
def index():
    return render_template('analysis/index.html')

@analysis_bp.route('/network_visualize')
def network_visualize():
    # with open('./output/test.csv', 'r') as f:
    #     lines = f.read().strip().split('\n')
    # edges = []
    # for line in lines:
    #     edge = line.split(',')
    #     edges.append(edge)
    # return json.dumps(edges)
    # return render_template('analysis/_network_visualize.html', data=1)
    return jsonify(data=1)

@analysis_bp.route('/reports_track')
def reports_track():
    # return render_template('analysis/_reports_track.html', data=2)
    return jsonify(data=2)
