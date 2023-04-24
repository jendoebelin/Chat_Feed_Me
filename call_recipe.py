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
        temp_line_width, _ = font.getbbox(temp_line.strip())[2:]
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

    # Add the recipe text to the right side of the image
    font = ImageFont.truetype("arial.ttf", 14)
    
    # Wrap the recipe text to fit the width of the background
    max_text_width = (image.width * 2) - 20
    wrapped_text = wrap_text(recipe_text, font, max_text_width)

    # Calculate the required height based on the number of lines in the wrapped text
    line_spacing = 2
    required_height = (len(wrapped_text.split("\n")) + 1) * (font.getbbox("A")[3] + line_spacing)

    # Create a white background image with the required height
    bg_width, bg_height = image.size
    background = Image.new("RGB", (bg_width * 3, max(required_height, bg_height)), "black")

    # Calculate the vertical offset needed to center the image
    image_vertical_offset = (background.height - image.height) // 2

    # Paste the original image onto the background, with the vertical offset
    background.paste(image, (0, image_vertical_offset))

    draw = ImageDraw.Draw(background)

    # Add line_spacing between lines
    y_offset = 10
    for line in wrapped_text.split("\n"):
        draw.text((bg_width + 10, y_offset), line, font=font, fill="white")
        y_offset += font.getbbox("A")[3] + line_spacing

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
    #output_filename = "output_image.png"
    output_filename = prompt.replace(',', '').replace('.', '') + ".png"

    # Read the contents of the recipe.txt file
    recipe_text = get_recipe_text("recipe.txt")

    save_base64_image_to_png(result, output_filename, recipe_text)
    #if result is not None:
        #print("Stable Diffusion API response:", result)

# Display the saved image
    image = Image.open(output_filename)
    image.show()