import pandas as pd
import requests
import json
import random
import csv

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
    # Shuffle the food items randomly
    #random.shuffle(food_items)
    food_items.sort()

    return food_items

def save_missing_ingredients_to_csv(missing_ingredients, filename="missing.csv"):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        for ingredient in missing_ingredients:
            csv_writer.writerow([ingredient['name']])

def get_recipe_suggestions(ingredients, api_key):
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": api_key,
        "ingredients": ",".join(ingredients)
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipe_suggestions = response.json()
        for recipe in recipe_suggestions:
            # Count the number of missing ingredients in the recipe
            missing_ingredients = [i for i in recipe['missedIngredients'] if i['name'].lower() not in ingredients]
            recipe['missingIngredientCount'] = len(missing_ingredients)
        
        # Sort the list of recipes by the count of missing ingredients, with the least missing ingredients first
        recipe_suggestions = sorted(recipe_suggestions, key=lambda r: r['missingIngredientCount'])
        
        return recipe_suggestions
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

        
def pretty_print_recipe(recipe_details, missing_ingredients, used_ingredients): 
    all_ingredients = missing_ingredients + used_ingredients
    save_recipe_ingredients_to_csv(all_ingredients, "recipe_ingredients.csv")
    recipe_text = f"\nRecipe: {recipe_details['title']}\n"
    recipe_text += f"Servings: {recipe_details['servings']}\n"
    recipe_text += f"Ready in {recipe_details['readyInMinutes']} minutes\n"

    recipe_text += "\nMissing ingredients:\n"
    for ingredient in missing_ingredients:
        recipe_text += f"- {ingredient['name']}\n"

    recipe_text += "\nIngredients you have:\n"
    for ingredient in used_ingredients:
        recipe_text += f"- {ingredient['name']}\n"

    recipe_text += "\nInstructions:\n"
    if 'analyzedInstructions' in recipe_details and len(recipe_details['analyzedInstructions']) > 0:
        for idx, step in enumerate(recipe_details['analyzedInstructions'][0]['steps']):
            recipe_text += f"{idx + 1}. {step['step']}\n"
    else:
        recipe_text += "No detailed instructions available.\n"

    recipe_text += f"\nFor more details, visit: {recipe_details['sourceUrl']}\n"
    
    print(recipe_text)
    return recipe_text

def save_recipe_ingredients_to_csv(ingredients, filename="recipe_ingredients.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["food"])  # Write the header
        for ingredient in ingredients:
            csv_writer.writerow([ingredient['name']])
            
def main():
    food_items = load_food_items_from_csv(CSV_FILENAME)
    recipe_suggestions = get_recipe_suggestions(food_items, API_KEY)

    if len(recipe_suggestions) == 0:
        print("No recipe suggestions found.")
        return

    print(f"Here are {len(recipe_suggestions)} recipe suggestions:")
    for index, recipe in enumerate(recipe_suggestions):
        print(f"{index + 1}. {recipe['title']} (missing {recipe['missingIngredientCount']} ingredients)")

    # Ask the user to pick a recipe and save the choice to best_choice
    best_choice = int(input("\nPick a recipe by entering its number: ")) - 1

    # Retrieve the entire recipe from the API
    recipe_id = recipe_suggestions[best_choice]['id']
    recipe_details = get_recipe_details(API_KEY, recipe_id)

    if recipe_details is not None:
        print("\nHere are the details for the chosen recipe:")
        recipe_text = pretty_print_recipe(recipe_details,
                            recipe_suggestions[best_choice]['missedIngredients'],
                            recipe_suggestions[best_choice]['usedIngredients'])
        
        # Save the missing ingredients to the CSV file
        save_missing_ingredients_to_csv(recipe_suggestions[best_choice]['missedIngredients'])
    while True:
            user_input = input("\nPress 'q' to quit or 'p' to save the recipe to a file: ").lower()

            if user_input == 'q':
                break
            elif user_input == 'p':
                with open("recipe.txt", "w") as file:
                    file.write(recipe_text)
                print("Recipe saved to recipe.txt")
                break
            else:
                print("Invalid input. Please enter 'q' or 'p'.")
    else:
        print("Could not retrieve recipe details.")
    


    
if __name__ == "__main__":
    main()

