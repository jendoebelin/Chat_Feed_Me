import pandas as pd
import random
import requests
import json
import base64
from PIL import Image
from io import BytesIO
from PIL import ImageDraw, ImageFont
import os

def get_random_items(filename, num_items):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)

    # Get a list of items from the 'food' column
    items = df['food'].tolist()

    # Select a specified number of random items
    random_items = random.sample(items, num_items)

    return random_items

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

def save_base64_image_to_png(base64_string, output_filename, items):
    # Decode the base64 string
    decoded_image = base64.b64decode(base64_string)

    # Convert the decoded bytes to an image using BytesIO
    image_data = BytesIO(decoded_image)
    image = Image.open(image_data)

    # Create a black background image
    bg_width, bg_height = image.size
    background = Image.new("RGB", (bg_width * 2, bg_height), "black")

    # Paste the original image onto the background
    background.paste(image, (0, 0))

    # Add the items to the right side of the image
    draw = ImageDraw.Draw(background)
    item_locations = []

    for item in items:
        font_size = random.randint(20, 60)
        font = ImageFont.truetype("arial.ttf", font_size)
        item_width, item_height = font.getbbox(item)[2:]

        # Find a suitable location for the text, avoiding overlaps and out of space
        while True:
            x = random.randint(bg_width + 10, max(bg_width + 11, bg_width * 2 - 20 - item_width))
            y = random.randint(10, bg_height - 20 - item_height)
            new_location = (x, y, x + item_width, y + item_height)

            # Check for collision
            collision = False
            for loc in item_locations:
                if (new_location[0] < loc[2] and new_location[2] > loc[0] and
                        new_location[1] < loc[3] and new_location[3] > loc[1]):
                    collision = True
                    break

            if not collision:
                item_locations.append(new_location)
                break

        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Draw the item text
        draw.text((x, y), item, font=font, fill=color)

    # Save the new image as a PNG file
    background.save(output_filename, 'PNG')
    
def create_stable_diffusion_prompt(items):
    # Create a stable diffusion prompt using the items
    prompt = f"Cooking {', '.join(items[:-1])}, and {items[-1]}."
    
    return prompt

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
        "cfg_scale":9
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
    #items = ['eggs','flour','bread','milk','sugar','salt','pepper','cheese','lettuce','tomato']
    # Get 5 random items from missing.csv
    script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_file_path = os.path.join(script_dir, "missing.csv")
    try:
        items = get_random_items(csv_file_path, 10)
    except Exception as e:
        print(f"Error occurred while getting random items: {e}")
        items = ['eggs','flour','bread','milk','sugar','salt','pepper','cheese','lettuce','tomato']  # Assign an empty list to items if an error occurs

    #items = get_random_items(csv_file_path, 5)
    #print(items)
    prompt = create_stable_diffusion_prompt(items)
    print("Generated prompt:", prompt)

    result = get_img(prompt)
    #output_filename = "output_image.png"
    output_filename = prompt.replace(',', '').replace('.', '') + ".png"

    
    # Convert the list of items into a single string
    items_text = "\n".join(items)

    save_base64_image_to_png(result, output_filename, items)
    #if result is not None:
     #   print("Stable Diffusion API response:", result)

# Display the saved image
    image = Image.open(output_filename)
    image.show()