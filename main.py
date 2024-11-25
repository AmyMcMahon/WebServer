import sys
import logging
import json
import time
from lib_config.config import Config
from lib_utils.blocktimer import BlockTimer
from datetime import datetime, UTC
from lib_metrics_datamodel.metrics_datamodel import Device, DataSnapshot
from flask import Flask, request, jsonify
from threading import Lock
from enum import Enum
import uuid


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


# class CachedData:
#     def __init__(self, cache_duration_seconds: int = 30):
#         self.data = None
#         self.cache_duration_seconds = cache_duration_seconds
#         self.last_updated = time.monotonic() - self.cache_duration_seconds
#         self.lock = Lock()

#     def __enter__(self):
#         self.lock.acquire()
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.lock.release()

#     def is_expired(self) -> bool:
#         return time.monotonic() - self.last_updated >= self.cache_duration_seconds

#     def update(self, data: any):
#         self.data = data
#         self.last_updated = datetime.now(UTC)


class Application:
    def __init__(self):
        self.config = Config(__file__)
        self.logger = logging.getLogger(__name__)
        # self.cached_data = CachedData(self.config.web.cache_duration_seconds)
        self.people = {}
        self.webserver = Flask(__name__)
        self.setup_routes()
        self.logger.debug("Application initialized")

    def run(self) -> int:
        try:
            self.logger.info(
                "Starting Flask web server on port %s", self.config.web.port
            )
            self.webserver.run(debug=self.config.web.debug, port=self.config.web.port)
            self.logger.info("Application completed successfully")
            return 0

        except Exception as e:
            self.logger.exception("Application failed with error: %s", str(e))
            return 1

    def setup_routes(self):
        self.webserver.route("/hello")(self.hello_world)
        # self.webserver.route("/metrics")(self.metrics)
        self.webserver.route(
            "/people", methods=[HttpMethod.GET.value, HttpMethod.POST.value]
        )(self.handle_people)
        self.webserver.route(
            "/people/<person_id>",
            methods=[
                HttpMethod.GET.value,
                HttpMethod.PUT.value,
                HttpMethod.DELETE.value,
            ],
        )(self.handle_person)

    def hello_world(self):
        self.logger.info("Hello world route called")
        return {"message": "Hello, World!"}

    def handle_people(self):
        """Handle /people endpoint for GET and POST methods."""
        if request.method == HttpMethod.GET.value:
            self.logger.info("Getting all people")
            return jsonify(list(self.people.values())), 200

        elif request.method == HttpMethod.POST.value:
            person = request.get_json()
            if not person or "name" not in person or "dob" not in person:
                return jsonify({"error": "Name and DoB required"}), 400

            person_id = str(uuid.uuid4())
            person["id"] = person_id
            self.people[person_id] = person
            self.logger.info(f"Created new person with ID {person_id}")
            return jsonify(person), 201

    def handle_person(self, person_id):
        """Handle /people/<person_id> endpoint for GET, PUT and DELETE methods."""
        if request.method == HttpMethod.GET.value:
            if person_id not in self.people:
                return jsonify({"error": "Person not found"}), 404

            self.logger.info(f"Getting person {person_id}")
            return jsonify(self.people[person_id])

        elif request.method == HttpMethod.PUT.value:
            if person_id not in self.people:
                return jsonify({"error": "Person not found"}), 404

            person = request.get_json()
            if not person or "name" not in person or "dob" not in person:
                return jsonify({"error": "Name and DoB required"}), 400

            person["id"] = person_id
            self.people[person_id] = person
            self.logger.info(f"Updated person {person_id}")
            return jsonify(person)

        elif request.method == HttpMethod.DELETE.value:
            # Structured so a delete of something already deleted doesn't cause an error
            if person_id in self.people:
                del self.people[person_id]

            self.logger.info(f"Deleted person {person_id}")
            return "", 204

    # def metrics(self):
    #     self.logger.info("Metrics route called")
    #     conversion_method = request.args.get("conversion_method", default=0, type=int)
    #     try:
    #         with self.cached_data, BlockTimer("read_metrics", self.logger):
    #             if self.cached_data.is_expired():
    #                 self.logger.info("Cache expired, reading new data")
    #                 data_snapshot = Device.read_PC_metrics()
    #                 self.cached_data.update(data_snapshot)
    #             else:
    #                 self.logger.info("Serving cached data")
    #                 data_snapshot = self.cached_data.data

    #             # Object direct to dict() for flask to do the only JSON string conversion
    #             rest_ready_json = data_snapshot.to_dict()

    #             timestamp = datetime.now(UTC).isoformat()

    #         return {
    #             "status": "success",
    #             "data": rest_ready_json,
    #             "timestamp": timestamp,
    #         }, 200
    #     except Exception as e:
    #         self.logger.exception("Metrics route failed with error: %s", str(e))
    #         return {"error": str(e)}


def main() -> int:
    """Entry point for the application."""
    app = Application()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
