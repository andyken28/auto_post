from app import create_app


app = create_app()


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Use port 8080 as requested
    # Use reloader off in production; keep debug tied to config
    debug = app.config.get("DEBUG", False)
    app.run(host="0.0.0.0", port=8080, debug=debug)
