"""
Controller for routes
"""
from flask import jsonify, url_for, abort
from service import app
from service.common import status

COUNTER = {}


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


############################################################
# Index page
############################################################
@app.route("/")
def index():
    """Returns information about the service and available endpoints"""
    app.logger.info("Request for Base URL")

    # Detailed service information for "Discovery"
    return jsonify(
        service_name="Hit Counter Service",
        version="1.1.0",
        status="OK",
        description="A lightweight microservice for tracking hit counters in real-time.",
        endpoints={
            "root": {
                "url": url_for("index", _external=True),
                "method": "GET",
                "description": "This discovery page"
            },
            "health": {
                "url": url_for("health", _external=True),
                "method": "GET",
                "description": "Health check for the service"
            },
            "list_counters": {
                "url": url_for("list_counters", _external=True),
                "method": "GET",
                "description": "Get a list of all active counters"
            },
            "create_counter": {
                "url": url_for("list_counters", _external=True) + "/<name>",
                "method": "POST",
                "description": "Initialize a new counter with zero count"
            },
            "read_counter": {
                "url": url_for("list_counters", _external=True) + "/<name>",
                "method": "GET",
                "description": "Read the current value of a specific counter"
            },
            "update_counter": {
                "url": url_for("list_counters", _external=True) + "/<name>",
                "method": "PUT",
                "description": "Increment the value of a specific counter by 1"
            },
            "delete_counter": {
                "url": url_for("list_counters", _external=True) + "/<name>",
                "method": "DELETE",
                "description": "Permanently remove a counter"
            }
        },
        service_stats={
            "total_counters": len(COUNTER),
            "running_environment": "Docker Container"
        }
    )


############################################################
# List counters
############################################################
@app.route("/counters", methods=["GET"])
def list_counters():
    """Lists all counters"""
    app.logger.info("Request to list all counters...")

    counters = [dict(name=count[0], counter=count[1]) for count in COUNTER.items()]

    return jsonify(counters)


############################################################
# Create counters
############################################################
@app.route("/counters/<name>", methods=["POST"])
def create_counters(name):
    """Creates a new counter"""
    app.logger.info("Request to Create counter: %s...", name)

    if name in COUNTER:
        return abort(status.HTTP_409_CONFLICT, f"Counter {name} already exists")

    COUNTER[name] = 0

    location_url = url_for("read_counters", name=name, _external=True)
    return (
        jsonify(name=name, counter=0),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


############################################################
# Read counters
############################################################
@app.route("/counters/<name>", methods=["GET"])
def read_counters(name):
    """Reads a single counter"""
    app.logger.info("Request to Read counter: %s...", name)

    if name not in COUNTER:
        return abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    counter = COUNTER[name]
    return jsonify(name=name, counter=counter)


############################################################
# Update counters
############################################################
@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name):
    """Updates a counter"""
    app.logger.info("Request to Update counter: %s...", name)

    if name not in COUNTER:
        return abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    COUNTER[name] += 1

    counter = COUNTER[name]
    return jsonify(name=name, counter=counter)


############################################################
# Delete counters
############################################################
@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name):
    """Deletes a counter"""
    app.logger.info("Request to Delete counter: %s...", name)

    if name in COUNTER:
        COUNTER.pop(name)

    return "", status.HTTP_204_NO_CONTENT


############################################################
# Utility for testing
############################################################
def reset_counters():
    """Removes all counters while testing"""
    global COUNTER  # pylint: disable=global-statement
    if app.testing:
        COUNTER = {}
