# import requests
# from constants import *
# import json
# from routeOpt import get_Optimized_locations


# def update_card_position(card_id, pos):
#     url = f"{BASE_URL}cards/{card_id}"
#     query = {
#         'key': API_KEY_trello,
#         'token': TOKEN_trello,
#         'pos': pos
#     }
#     response = requests.put(url, params=query)
#     return response.json()

# def swap_card_positions(source_card_id, target_card_id):
#     # Get the positions of both cards
#     source_card_pos = requests.get(f"{BASE_URL}cards/{source_card_id}", params={'key': API_KEY_trello, 'token': TOKEN_trello}).json()['pos']
#     target_card_pos = requests.get(f"{BASE_URL}cards/{target_card_id}", params={'key': API_KEY_trello, 'token': TOKEN_trello}).json()['pos']

#     # Swap the positions
#     update_card_position(source_card_id, target_card_pos)
#     update_card_position(target_card_id, source_card_pos)

#     print(f"Swapped card {source_card_id} with {target_card_id}")

# Origin = "1234 w jefferson street buckeye az 85326 usa"

# response  = requests.get(f"https://api.trello.com/1/lists/{list_id_Trelo}/cards?key={API_KEY_trello}&token={TOKEN_trello}")

# # with open('response.json',"w") as f:
# #     json.dump(response.json(),f,indent=4)
# results = response.json()

# allCards = {}
# cardLocations = []

# for result in results:
#     # print(f'CardID:{result["id"]},And cardLocation:{result['name']}')
#     # print("-"*40)
#     allCards[result['name']]=result['id']
#     cardLocations.append(result['name'])
# locs = list(allCards.keys())
# waypointsIndex,routeUrl = get_Optimized_locations(Origin,cardLocations)

# print('Opt_waypnts:',waypointsIndex)
# with open('opt_locations.txt','w') as f:
#     for index, rank in enumerate(waypointsIndex):
#         # print(f"Location:{cardLocations[rank]}, CardID:{allCards[cardLocations[rank]]}")
#         # print('Confirm location:',locs[rank])
#         # print("-"*40)
#         source_card_id = allCards[cardLocations[rank]]
        
#         target_card_id = allCards[cardLocations[index]]
#         if cardLocations[rank]==locs[rank]:
#             swap_card_positions(source_card_id,target_card_id)
#             print(f"Card:{cardLocations[rank]} is Set at :{index+1}")
#             f.write(locs[rank]+'\n')




import requests
from constants import *
import json
from routeOpt import get_Optimized_locations


def update_card_position(card_id, pos):
    url = f"{BASE_URL}cards/{card_id}"
    query = {
        'key': API_KEY_trello,
        'token': TOKEN_trello,
        'pos': pos
    }
    response = requests.put(url, params=query)
    return response.json()

Origin = "1234 w jefferson street buckeye az 85326 usa"

response = requests.get(f"https://api.trello.com/1/lists/{list_id_Trelo}/cards?key={API_KEY_trello}&token={TOKEN_trello}")
results = response.json()

allCards = {}
cardLocations = []

# Collect all card IDs and names
for result in results:
    allCards[result['name']] = result['id']
    cardLocations.append(result['name'])

with open('oldLocation.txt','w') as f:
    for loc in cardLocations:
        f.write(loc+'\n')

# Get optimized locations
waypointsRank, routeUrl = get_Optimized_locations(Origin, cardLocations)

# Prepare to update the positions
new_positions = []
opt_locations = []
for rank in waypointsRank:
    new_positions.append(allCards[cardLocations[rank]])
    opt_locations.append(cardLocations[rank])
with open('opt_ocations.txt','w') as f:
    for loc in opt_locations:
        f.write(loc+'\n')
# Update all cards based on the optimized order
for i, card_id in enumerate(new_positions):
    # Positions are usually set by the order of appearance in the list
    # Set each card's position in the optimized order
    update_card_position(card_id, i + 1)  # Use (i + 1) to set position

print('Cards have been rearranged based on optimized locations.')
