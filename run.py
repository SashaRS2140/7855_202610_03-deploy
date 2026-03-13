from src.server import create_app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    # Host '0.0.0.0' makes the server accessible to other devices (like your phone)
    # on the same Wi-Fi network.
    app.run(host='0.0.0.0', port=5000, debug=True)