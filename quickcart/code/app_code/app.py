
import os
from flask import Flask, render_template, request,render_template,jsonify
from validation import compact_mode_check,validate_style
from flask_wtf.csrf import CSRFProtect
from audit import md_check
from error_handling import ErrorHandler
from internal_authentication import log_request_authenticated
from log_file_handler import write_log,read_logs,read_last_log
from werkzeug.exceptions import HTTPException
def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("APP_SECRET"),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    csrf = CSRFProtect(app)

    products = (
        {"name": "Canvas Tote", "price": "18.00", "description": "A simple everyday carry bag."},
        {"name": "Desk Mug", "price": "12.50", "description": "A sturdy ceramic mug for work breaks."},
        {"name": "Pocket Notes", "price": "6.00", "description": "A compact notebook for quick ideas."},
    )

    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        if isinstance(error, HTTPException):
            return error
        return ErrorHandler.handle_error(error)
        
    
    @app.after_request
    def add_default_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; img-src 'self'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        return response

    @app.get("/")
    def home():
        query = request.args.get("q", "").strip()[:80]
        visible = products
        if query:
            needle = query.casefold()
            visible = tuple(p for p in products if needle in p["name"].casefold())
        return render_template("index.html", products=visible, query=query)

    @app.route("/receipt", methods=["GET", "POST"])
    def receipt():
        message = "Thanks for shopping with QuickCart."
        style = ""

        if request.method == "POST":
            style = request.form.get("style", "standard")
            message = request.form.get("message", "").strip()[:200]
            if not validate_style(style):
               style = "standard"

            if style != "standard":
                return compact_mode_check(message)
            return render_template("receipt_preview.html", message=message, style=style)
        
        return render_template("receipt.html", message=message, style=style)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.route("/error")
    @app.route("/error/<mode>")
    def error_page(mode=""):
        last_error=""
        try:
            if mode=="audit":
                record = read_last_log()
                if record:
                    last_error = record.get("error")
            app.logger.error("Application error: %s", "system_error_occured")
        except Exception:
            app.logger.error("Invalid encoded error received")

        return render_template(
                "error.html",
                last_error=last_error,
            ), 500

    @app.route("/audit/<mode>")
    @md_check
    def check_if_audit():
        return render_template("receipt_internal.html")

    @app.post("/log-error")
    @csrf.exempt
    def log_error():
        body = request.get_data(cache=True)

        if not log_request_authenticated(body):
            return {"error": "unauthorized"}, 401

        if not request.is_json:
            return {
                "error": "application/json required"
            }, 415

        payload = request.get_json(
            silent=True
        ) or {}

        if set(payload) != {"error_log"}:
            return {
                "error": "invalid payload"
            }, 400

        error_log = payload.get("error_log")

        if (
            not isinstance(error_log, str)
            or not error_log.strip()
        ):
            return {
                "error": "error_log is required"
            }, 400

        write_log(error_log)

        return {
            "status": "logged"
        }, 201


    @app.get("/logs")
    def get_logs():

        body = request.get_data(cache=True)

        if not log_request_authenticated(body):
            return {"error": "unauthorized"}, 401

        try:
            limit = int(
                request.args.get("limit", "100")
            )

        except ValueError:
            return {
                "error": "limit must be an integer"
            }, 400

        if not 1 <= limit <= 200:
            return {
                "error": "limit must be between 1 and 200"
            }, 400

        response = jsonify({
            "logs": read_logs(limit)
        })

        response.headers[
            "Cache-Control"
        ] = "no-store"

        response.headers[
            "Pragma"
        ] = "no-cache"

        return response
    return app

app = create_app()
