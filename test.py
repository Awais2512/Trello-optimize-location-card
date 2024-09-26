import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
from routeOpt import get_Optimized_locations
import re
from constants import *


# Chrome options for the undetected driver to prevent detection by Trello
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--start-maximized")
# Initialize the driver
driver = uc.Chrome(options=chrome_options)


# Normalize the Text of the location To Avoid Format conflict Error

def normalize_address(address):
    # Define a dictionary for abbreviations
    abbreviations = {
        "dr": "drive",
        "ave": "avenue",
        "blvd": "boulevard",
        "rd": "road",
        "st": "street",
        "ln": "lane",
        "e": "east",
        "w": "west",
        "s": "south",
        "n": "north",
        "village": "",
        "unit": "",
        "apt": "",
        "#": "",  # Remove hash symbol
        "-": "",  # Remove dash symbol
        ",": "",  # Remove commas
    }

    # Handle specific cases for spelling normalization (e.g., "shangri la" to "shangrila")
    special_cases = {
        r'\bshangri la\b': 'shangrila'
    }

    # Remove unwanted characters like commas and replace special cases
    for abbr, full in abbreviations.items():
        address = re.sub(rf'\b{abbr}\b', full, address, flags=re.IGNORECASE)

    # Apply special case replacements
    for pattern, replacement in special_cases.items():
        address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)

    # Normalize zip codes: only keep the first 5 digits
    address = re.sub(r'(\d{5})\d{3,4}', r'\1', address)

    # Remove special characters (except for alphanumeric and space) and normalize spaces
    address = re.sub(r'[^a-zA-Z0-9\s]', '', address)

    # Convert to lowercase and remove excess whitespace
    return re.sub(r'\s+', ' ', address.strip()).lower()


# Example:
# "6435 W Fawn Dr, Laveen Village, AZ 85339, USA" --> "6435 w fawn drive laveen az 85339 usa"


# Function to log into Trello manually using credentials
def login_manually(driver):
    login_btn = driver.find_element(By.CSS_SELECTOR,'a[data-uuid="MJFtCCgVhXrVl7v9HA7EH_login"]')
    login_btn.click()
    login_btn = driver.find_element(By.ID,'google-auth-button')
    login_btn.click()
    login_user = driver.find_element(By.ID,'identifierId')
    login_user.send_keys(username_trello)  # Replace with your email
    login_user.send_keys(Keys.ENTER)
    login_pass = driver.find_element(By.CSS_SELECTOR,'input[aria-label="Enter your password"]')
    time.sleep(2)
    login_pass.send_keys(password_trello)  # Replace with your password
    login_pass.send_keys(Keys.ENTER)
    time.sleep(2)
    driver.get(listing_board_url) #Replace The url with YOUr own Trello Board
    time.sleep(2)
    save_cookies(driver)


# Function to save browser cookies to avoid logging in every time
def save_cookies(driver):
    cookies = driver.get_cookies()
    with open('cookies.json', 'w') as file:
        json.dump(cookies, file)


# Function to login to Trello using saved cookies
def login_trelo(driver):
    driver.implicitly_wait(10)
    driver.maximize_window()
    driver.get("https://trello.com/")

    # Load cookies from file to skip manual login
    with open('cookies.json', 'r') as file:
        cookies = json.load(file)
    
    # Add cookies to the browser session
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    
    # Reload the page after adding cookies
    driver.refresh()
    
    time.sleep(2)
    driver.get(listing_board_url) #Replace The url with YOUr own Trello Board
    time.sleep(2)

# Function to drag and drop Trello cards
def drag_and_drop_card(driver, source_element, target_element):
    actions = ActionChains(driver)
    # actions.click_and_hold(source_element).move_to_element(target_element).release().perform()
    ActionChains(driver).drag_and_drop(source_element, target_element).perform()



# Function to retrieve and rearrange cards based on a new randomized order
def get_and_swap_locations(Origin:str,list_name: str):
    # Find the Trello list by name
    card_lists = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="list"]')
    card_list = None
    
    # Find the specific list by matching list names
    for list_element in card_lists:
        list_title = list_element.find_element(By.CSS_SELECTOR, 'h2[data-testid="list-name"]').text.lower()
        if list_title == list_name.lower():
            print('List Found:', list_title)
            card_list = list_element
            break

    # If list is not found, return
    if not card_list:
        print(f"List '{list_name}' not found.")
        return

    # Get all cards in the list
    cards = card_list.find_elements(By.CSS_SELECTOR, 'li[data-testid="list-card"]')
    print("Total cards in the List:", len(cards))

    locations = []

     # Collect the text from each card and save it to a file
    for card in cards:
        card_text = card.text
        print(card_text)
        if card_text not in locations:
            locations.append(card_text)
    
    with open('oldLocation.txt', 'w') as f:
        for location in locations:
            f.write(location + "\n")

    # Get optimized locations
    waypoint_order , opt_route = get_Optimized_locations(Origin, locations)
    
    print("Total Number of Rearranged Locations:",len(waypoint_order))

    #Getting the card elements for the target location for card swapping
    upd_cards = card_list.find_elements(By.CSS_SELECTOR, 'li[data-testid="list-card"]')

    # # the following logic is for Copying the card from one bourd to another in opt-sequence
    # for place in reversed(waypoint_order):
    #     print(f"The Number of Waypoint order:{place}")
    #     card = cards[place]
    #     copy_opt_cards(card)
    #     print(f'The card Copied: {card.text}')
    print("TyPe of Cards element:",type(cards))


    #The following logic is Swap the cards and arrange them according to opt-sequence
    for i, location in enumerate(waypoint_order):
        # normalized_location = normalize_address(location)
        # normalized_location = location
        # source_card = card_map.get(normalized_location)
        source_card = cards[location]

        if not source_card:
            print(f"Source card for location '{location}' not found.")
            continue

        # if i < len(waypoint_order) - 1:
            # target_location = new_locations[i + 1]
            # normalized_target_location = target_location
            # target_card = card_map.get(normalized_target_location)
        target_card = upd_cards[i]
        # else:
        #     print("Card not found to Swap")
        #     target_card = None  # No target for the last card

        if source_card.text==target_card.text:
            print("Cards are same so we skip this:",source_card.text)
            continue
        # Perform drag and drop if target exists
        if target_card and source_card:
            drag_and_drop_card(driver, source_card, target_card)
            print(f"source Index:{location},Target Index:{i},Card:{source_card.text}")
            time.sleep(2)
        

        #Getting the new sequence of the cards after swaping one Card
        upd_cards = card_list.find_elements(By.CSS_SELECTOR, 'li[data-testid="list-card"]')
           
    return waypoint_order , opt_route 


def posting_opt_board(Optimized_waypoints:list):
    driver.get('https://trello.com/b/AbPZtWQb/optimized-board')
    opt_list = driver.find_element(By.CSS_SELECTOR,'div[data-testid="list"]')
    opt_list.find_element(By.CSS_SELECTOR,'button[data-testid="list-add-card-button"]').click()

    for location in reversed(Optimized_waypoints):      
           
        card_in = opt_list.find_element(By.CSS_SELECTOR,'[data-testid="list-card-composer-textarea"]')
        card_in.send_keys(location)
        time.sleep(2)
        card_in.send_keys(Keys.ENTER)

    print("All Optimize Loctions are added to cards")
    driver.refresh()
        
def copy_opt_cards(card):
    card.click()
    driver.find_element(By.CSS_SELECTOR,'a[title="Copy"]').click()
    board_name = driver.find_element(By.CSS_SELECTOR,'div[data-testid="move-card-popover-select-board-destination"]')
    board_name.click()
    bourd_in =  driver.switch_to.active_element #board_name.find_element(By.CSS_SELECTOR,'input[react-select-11-input]')
    bourd_in.send_keys('Opti'+Keys.ENTER)
    # Keys.ENTER
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR,'button[data-testid="move-card-popover-move-button"]').click()
    driver.back()




def main():
    list_name = "Done"
    Origin = "1234 w jefferson street buckeye az 85326 usa"


    try:
        # Log into Trello using the previously saved cookies
        login_trelo(driver)
    except:
        # Log Manually by gmail id and password 
        login_manually(driver)
    
    # copy_opt_cards()
    # Specify the Trello list name and get locations
    waypoint_order , opt_route  = get_and_swap_locations(Origin,list_name)

    
    print('Opt Waypoints:',waypoint_order)
    print("Route Link:",opt_route)
    # driver.get(opt_route)
    print("!!!!Swapping Completed!!!!")
    input("!!!!*****Enter To Quit*****!!!!")

    # Close the browser session
    driver.quit()

 


main()


# start = '23000 north 231st avenue wittmann az 85361 usa'
# end = '5940 west park view lane glendale az 85310 usa'


# find_map_directions(start,end)
# input("!!!!******Press Enter*******!!!!!")
driver.quit()