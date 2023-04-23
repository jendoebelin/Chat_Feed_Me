import pandas as pd
import requests
import json

def read_api_key_from_file(filename):
    with open(filename, 'r') as file:
        api_key = file.read().strip()
    return api_key

API_KEY = read_api_key_from_file("api_key.txt") #Put your API key in the api_key.txt file
CSV_FILENAME = "food_items.csv"

def get_recipe_details(api_key, recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        recipe_details = response.json()
        return recipe_details
    else:
        print(f"Error: {response.status_code}")
        return None

def load_food_items_from_csv(filename):
    df = pd.read_csv(filename)
    food_items = df["food"].tolist()
    return food_items


def get_recipe_suggestions(ingredients, api_key, count=3):
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": api_key,
        "ingredients": ",".join(ingredients),
        "number": count,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")
        
def pretty_print_recipe(recipe_details):
    print(f"\nRecipe: {recipe_details['title']}")
    print(f"Servings: {recipe_details['servings']}")
    print(f"Ready in {recipe_details['readyInMinutes']} minutes")

    print("\nIngredients:")
    for ingredient in recipe_details['extendedIngredients']:
        print(f"- {ingredient['original']}")

    print("\nInstructions:")
    if 'analyzedInstructions' in recipe_details and len(recipe_details['analyzedInstructions']) > 0:
        for idx, step in enumerate(recipe_details['analyzedInstructions'][0]['steps']):
            print(f"{idx + 1}. {step['step']}")
    else:
        print("No detailed instructions available.")

    print(f"\nFor more details, visit: {recipe_details['sourceUrl']}")

def main():
    food_items = load_food_items_from_csv(CSV_FILENAME)
    recipe_suggestions = get_recipe_suggestions(food_items, API_KEY)

    print(f"Here are {len(recipe_suggestions)} recipe suggestions:")
    for index, recipe in enumerate(recipe_suggestions):
        print(f"{index + 1}. {recipe['title']}")

  

    # Ask the user to pick a recipe and save the choice to best_choice
    best_choice = int(input("\nPick a recipe by entering its number: ")) - 1

    # Retrieve the entire recipe from the API
    recipe_id = recipe_suggestions[best_choice]['id']
    recipe_details = get_recipe_details(API_KEY, recipe_id)

    print("\nHere are the details for the chosen recipe:")
    pretty_print_recipe(recipe_details)


    
if __name__ == "__main__":
    main()

