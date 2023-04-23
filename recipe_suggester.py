import pandas as pd
import requests

def read_api_key_from_file(filename):
    with open(filename, 'r') as file:
        api_key = file.read().strip()
    return api_key

API_KEY = read_api_key_from_file("api_key.txt") #Put your API key in the api_key.txt file
CSV_FILENAME = "food_items.csv"


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


def main():
    food_items = load_food_items_from_csv(CSV_FILENAME)
    recipe_suggestions = get_recipe_suggestions(food_items, API_KEY)

    print(f"Here are {len(recipe_suggestions)} recipe suggestions:")
    for index, recipe in enumerate(recipe_suggestions):
        print(f"{index + 1}. {recipe['title']}")


if __name__ == "__main__":
    main()

