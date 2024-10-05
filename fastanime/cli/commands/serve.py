import click


@click.command(
    help="Command that automates the starting of the builtin fastanime server",
    epilog="""
\b
\b\bExamples:
# default
fastanime serve

# specify host and port
fastanime serve --host 127.0.0.1 --port 8080
""",
)
@click.option("--host", "-H", help="Specify the host to run the server on")
@click.option("--port", "-p", help="Check for the latest release", type=int)
def serve(host, port):
    import os
    import sys

    from ...constants import APP_DIR

    args = ["python", "-m", "fastapi", "run"]
    if host:
        args.extend(["--host", host])

    if port:
        args.extend(["--port", port])
    args.append(os.path.join(APP_DIR, "api"))
    os.execv(sys.executable, args)
