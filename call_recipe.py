import pandas as pd
import random
import requests
import json
import base64
from PIL import Image
from io import BytesIO
from PIL import ImageDraw, ImageFont

def wrap_text(text, font, max_width):
    lines = []
    words = text.split(' ')
    current_line = ''

    for word in words:
        temp_line = current_line + ' ' + word
        temp_line_width, _ = font.getsize(temp_line.strip())
        if temp_line_width <= max_width:
            current_line = temp_line
        else:
            lines.append(current_line.strip())
            current_line = word

    if current_line:
        lines.append(current_line.strip())

    return "\n".join(lines)
    
def get_items(filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)

    # Get a list of items from the 'food' column
    items = df['food'].tolist()

    return items
    
def get_recipe_text(filename):
    with open(filename, "r") as file:
        return file.read()
    
def create_stable_diffusion_prompt(items):
    # Create a stable diffusion prompt using the items
    prompt = f"Cooking {', '.join(items[:-1])}, and {items[-1]}."
    
    return prompt
    
def save_base64_image_to_png(base64_string, output_filename, recipe_text):
    # Decode the base64 string
    decoded_image = base64.b64decode(base64_string)

    # Convert the decoded bytes to an image using BytesIO
    image_data = BytesIO(decoded_image)
    image = Image.open(image_data)

    # Create a white background image
    bg_width, bg_height = image.size
    background = Image.new("RGB", (bg_width * 2, bg_height), "white")

    # Paste the original image onto the background
    background.paste(image, (0, 0))

    # Add the recipe text to the right side of the image
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("arial.ttf", 8)
    
    # Wrap the recipe text to fit the width of the background
    max_text_width = bg_width - 20
    wrapped_text = wrap_text(recipe_text, font, max_text_width)
    
    draw.text((bg_width + 10, 10), wrapped_text, font=font, fill="black")

    # Save the new image as a PNG file
    background.save(output_filename, 'PNG')    

def call_stable_diffusion_api(prompt):
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    #url = "http://localhost:7860" # Replace this with the URL of your locally hosted Stable Diffusion API
    payload = {"prompt": prompt}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"Error: {response.status_code}")
        return None


def get_img(prompt):
    img_url = None
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    try:
        payload = json.dumps({
        "prompt": prompt,
        "steps": 25, 
        "cfg_scale":7
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        r = response.json()
        #print(r)
        image_64 = r["images"][0]
        #for i in r['images']:
        #image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        #img_url = Image.open(io.BytesIO(base64.b64decode(image_64)))
        img_url = image_64
        
    except Exception as e:
        # if it fails (e.g. if the API detects an unsafe image), use a default image
        img_url = "https://pythonprogramming.net/static/images/imgfailure.png"
        print(e)
        
    return img_url





if __name__ == "__main__":
    items = get_items("recipe_ingredients.csv")

    prompt = create_stable_diffusion_prompt(items)
    print("Generated prompt:", prompt)

    result = get_img(prompt)
    output_filename = "output_image.png"

    # Read the contents of the recipe.txt file
    recipe_text = get_recipe_text("recipe.txt")

    save_base64_image_to_png(result, output_filename, recipe_text)
    if result is not None:
        print("Stable Diffusion API response:", result)