import pandas as pd
import requests

API_KEY = "ee9dd159124549a18c96a93f4bd752fa"  # Replace with your Spoonacular API key
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

