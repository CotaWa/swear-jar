import json
from collections import defaultdict

def load_database():
        dictionary = {}
        with open("data.json", "r") as fp:
                raw_data = fp.read()
#                print(raw_data)
                dictionary = json.loads(raw_data)
        return dictionary


def get_nested_defaultdict():
    result = defaultdict(lambda: defaultdict(int))
    if "user_word_counts" in db:
        stored_data = json.loads(db["user_word_counts"])
        for user_id, word_dict in stored_data.items():
            for word, count in word_dict.items():
                result[user_id][word] = count
    return result


def save_word_counts():
    data_to_save = {}
    for user_id, word_dict in user_word_counts.items():
        data_to_save[user_id] = dict(word_dict)



def final_save(data):
    with open("data_transfered.txt", "w") as file:
        json.dump(data, file)


db = load_database()
user_word_counts = get_nested_defaultdict()

keys = []
values = []

for user_id in user_word_counts:
    total = 0
    if user_id in user_word_counts:
        for phrase, count in user_word_counts[user_id].items():
            total += (count)
    print(f"{user_id}:{total}")
    keys.append(user_id)
    values.append(total)

new_database = {key: value for key, value in zip(keys, values)}
print(new_database)

final_save(new_database)
