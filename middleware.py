from flask import request, g


class Middleware:
    def __init__(self, app):
        self.app = app
        # Register the middleware with the Flask app
        app.before_request(self.capture_ip)

    def capture_ip(self):
        # Check for 'X-Forwarded-For' header if the app is behind a proxy/load balancer
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            # Take the first IP in the list if behind a proxy
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Fallback to the remote address
            ip = request.remote_addr

        # Store the IP address in Flask's `g` context
        g.user_ip = ip
        # Optionally log the IP for debugging
        self.app.logger.info(f"Captured IP: {ip} for path: {request.path}")