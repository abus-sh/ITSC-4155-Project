

def get_token_for_testing():
    """Function to obtain the user token in `/secrets/toke_testing.txt` for testing the API"""
    with open('../../secrets/token_testing.txt', 'r') as file:
        token = file.readline().strip()
    return token