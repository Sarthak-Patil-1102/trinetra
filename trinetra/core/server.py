"""Tiny local web server for the live dashboard (trinetra dashboard --serve)."""


def serve(render_fn, port=7000):
    """render_fn() returns fresh dashboard HTML (re-scans on each call)."""
    from flask import Flask, redirect

    app = Flask("trinetra-dashboard")

    @app.route("/")
    def index():
        return render_fn()

    @app.route("/rescan", methods=["POST"])
    def rescan():
        return redirect("/")

    print(f"\n  👁 Trinetra dashboard live at http://127.0.0.1:{port}  (Ctrl-C to stop)\n")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
