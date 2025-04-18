import json

# Load the data from JSON file
def load_database():
    with open("data.json", "r") as fp:
        raw_data = fp.read()
        dictionary = json.loads(raw_data)  # This will convert the outer JSON into a Python dictionary
        
        # Deserialize the 'user_word_counts' string into a dictionary
        if "user_word_counts" in dictionary:
            dictionary["user_word_counts"] = json.loads(dictionary["user_word_counts"])

    return dictionary

db = load_database()

# Initialize a variable to store the total sum
total_sum = 0

# Loop through the data
for main_key, subkeys in db.items():
#    print(f"Main key: {main_key}")
    
    # Ensure subkeys is a dictionary before accessing .items()
    if isinstance(subkeys, dict):  # Check if subkeys is a dictionary
        for sub_key, ids in subkeys.items():
#            print(f"  Subkey: {sub_key}")
            
            # Ensure ids is a dictionary before accessing .items()
            if isinstance(ids, dict):  # Check if ids is a dictionary
                for user_id, info in ids.items():
#                    print(f"    ID: {user_id}")
                    
                    # Debug: Show the structure of 'info'
#                    print(f"      info: {info} (type: {type(info)})")
                    
                    # Since info is a dictionary and the values are integers,
                    # just add them directly to the total_sum
                    if isinstance(info, dict):  # Check if info is a dictionary
                        for key, value in info.items():
#                            print(f"        {key}: {value}")
                            total_sum += value  # Add the value to the total sum
                    elif isinstance(info, int):  # In case info is just an integer (as per your case)
#                        print(f"        {info}")  # This would be just the integer
                        total_sum += info  # Directly add the integer
#                    else:
#                        print(f"      Unexpected structure for info: {info}")
#            else:
#                print(f"    Unexpected structure for ids: {ids}")
#    else:
#        print(f"  Expected a dictionary for subkeys, but got: {type(subkeys)}")
#        print(subkeys)  # Show the actual value for debugging

# Print the total sum of all numbers
print(f"Total amount of money owed: ${total_sum}")
print(f"That is {total_sum/110} gold bars at spawn.")
