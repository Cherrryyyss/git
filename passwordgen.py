import random
import string

user = int(input("Enter password length: "))
alphabet = string.ascii_letters + string.digits
password = []
for i in range(user):
    password_gen = random.choice(alphabet)
    password.append(password_gen)
clean_password = "".join(password)
print("Your generated password is ", password)