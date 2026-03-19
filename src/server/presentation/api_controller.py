from flask import Blueprint, jsonify, request, current_app

api_bp = Blueprint('api', __name__)


##########################################################################
###                        HELPER FUNCTIONS                            ###
##########################################################################


def get_hw_service():
    return current_app.hw_service


##########################################################################
###                        CUBE REST API                               ###
##########################################################################


@api_bp.route("/esp/telemetry", methods=["POST"])
def receive_telemetry():
    """Endpoint for ESP32 to send button presses/sensor data."""
    data = request.get_json()
    response = get_hw_service().process_telemetry(data)
    return jsonify(response)


@api_bp.route("/esp/config", methods=["GET"])
def get_config():
    """Endpoint for ESP32 to fetch settings."""
    return jsonify(get_hw_service().get_config())