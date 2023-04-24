# Chat_Feed_Me
This fetches ingredients from a .csv file and suggest a few recipes from an API. The list of suggested recipes is ordered by least missing ingredients first. then generates the full recipe based on the user's input and generates or ammends a file called missing.csv, with missing ingredients to that list.

![image](https://user-images.githubusercontent.com/119360121/233819148-978ddc8d-341c-4f11-af2c-d412b4be5b41.png)

Running missing_unique.py will remove duplicates from the food_items.csv as well as the missing.csv file. 
Running call_sd.py will take ten random items from the missing.csv file and send a call to a locally running copy of stable diffusion to create a unique image with word cloud.
![image](https://user-images.githubusercontent.com/119360121/233891187-9960ab41-4e12-4834-aa66-bbc96bee2035.png)


Running call_recipe.py will send a call to a locally running copy of stable diffusion to create a unique image with the last recipe saved into a recipe card. 
![image](https://user-images.githubusercontent.com/119360121/233890115-8eaa756e-591c-46a7-9fbb-1563a85f5eeb.png)
