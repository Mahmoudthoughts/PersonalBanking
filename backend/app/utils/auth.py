from flask_jwt_extended import create_access_token


def generate_token(user_id):
    """Generate a JWT for the given user ID."""
    # ``flask_jwt_extended`` requires the subject claim to be a string.
    # Casting ensures tokens are valid even if ``user_id`` is an integer.
    return create_access_token(identity=str(user_id))
