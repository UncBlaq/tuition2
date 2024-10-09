import random
import string

def generate_random_name(length = 10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# Example usage:
random_string = generate_random_name()
print(random_string)