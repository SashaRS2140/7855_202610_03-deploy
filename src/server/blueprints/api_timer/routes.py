from . import api_timer_bp
from flask import request, jsonify, current_app
from src.server.decorators.auth import require_jwt
from src.server.utils.validation import require_json_content_type
from src.server.utils.repository import get_task_preset


##########################################################################
###                        TIMER API ROUTES                            ###
##########################################################################


#-- MAY NOT NEED --#
@api_timer_bp.post("/timer/reset")
@require_jwt
def api_reset_timer(uid: str):

    # Get timer object
    timer = current_app.timer

    # checking for content error
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # parsing data from json
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # checking parsed data if valid
    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    # parsing preset data using task name
    preset_data = get_task_preset(uid, task_name)

    # parsing current time from preset data
    task_time = preset_data.get("task_time")

    # resetting time from preset_data
    timer.reset(task_time)

    # return success
    return jsonify({"task_time": task_time}), 200