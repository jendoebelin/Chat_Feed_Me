import pandas as pd
import random
import requests
import json
import base64
from PIL import Image
from io import BytesIO

def get_random_items(filename, num_items):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)

    # Get a list of items from the 'food' column
    items = df['food'].tolist()

    # Select a specified number of random items
    random_items = random.sample(items, num_items)

    return random_items

def save_base64_image_to_png(base64_string, output_filename):
    # Decode the base64 string
    decoded_image = base64.b64decode(base64_string)

    # Convert the decoded bytes to an image using BytesIO
    image_data = BytesIO(decoded_image)
    image = Image.open(image_data)

    # Save the image as a PNG file
    image.save(output_filename, 'PNG')
    
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
        "steps": 80, 
        "cfg_scale":3.5
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
    random_items = get_random_items("missing.csv", 5)
    prompt = create_stable_diffusion_prompt(random_items)
    print("Generated prompt:", prompt)

    #result = call_stable_diffusion_api(prompt)
    result = get_img(prompt)
    output_filename = "output_image.png"
    save_base64_image_to_png(result, output_filename)
    if result is not None:
        print("Stable Diffusion API response:", result)
