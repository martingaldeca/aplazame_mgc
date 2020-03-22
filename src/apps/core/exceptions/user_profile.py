class NotCommerceError(Exception):
    """
    Custom exception for invalid token.
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"NotCommerceError, {self.message} "
        else:
            return f"Only commerce or admin users allowed."
