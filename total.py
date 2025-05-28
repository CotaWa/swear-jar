import json

# Load the data from JSON file
def load_database():
    with open("data.json", "r") as fp:
        raw_data = fp.read()
        dictionary = json.loads(raw_data)
    return dictionary

db = load_database()

total = 0
for user in db:
    total += db[user]

print(f"Total is ${total}.")
print(f"That is {total/110} gold ingots at spawn.")
