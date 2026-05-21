import os

from flask import Flask, jsonify

from src.calling import start_calling_workflow
from src.logger import configure_logging


def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)

    @app.get("/")
    def health_check():
        return jsonify({"status": "ok", "message": "Server is running"})

    @app.post("/start-calling")
    def start_calling():
        try:
            summary = start_calling_workflow()
            return jsonify(summary), 200
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    @app.post("/dry-run")
    def dry_run():
        try:
            summary = start_calling_workflow(dry_run=True)
            return jsonify(summary), 200
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
