import random
number = random.randrange(1,5)
attemp = 3
for i in range(attemp):
    try:
        user = int(input("enter a number: "))
        if user == number:
            print("you got it!")
            break
        else:
            print("try again!")
    except ValueError:
        print("enter valid number ")
print("code executed successfully ")