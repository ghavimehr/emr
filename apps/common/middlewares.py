# apps/common/middlewares.py

class RealIPMiddleware:
    """
    If REMOTE_ADDR == 127.0.0.1 (our Caddy proxy), then
    use the first value of HTTP_X_FORWARDED_FOR instead.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        real = request.META.get("REMOTE_ADDR")
        if real == "127.0.0.1":
            xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
            if xff:
                # take only the leftmost, true client IP
                request.META["REMOTE_ADDR"] = xff.split(",", 1)[0].strip()
        return self.get_response(request)
