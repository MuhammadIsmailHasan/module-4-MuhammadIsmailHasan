def ok(data=None, message=None, status=200):
    """Success envelope: { status: true, message, data }.

    `status` is the HTTP status of the response line; it is not placed in the body.
    Mutating endpoints pass a descriptive message; reads default to "OK".
    """
    return {"status": True, "message": message or "OK", "data": data}
