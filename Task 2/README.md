# Task 2 - REST API

## Database Schema
The database is made of the following tables:

### recipes

    +--------------+---------------+------+-----+---------+----------------+
    | Field        | Type          | Null | Key | Default | Extra          |
    +--------------+---------------+------+-----+---------+----------------+
    | id           | int(11)       | NO   | PRI | NULL    | auto_increment |
    | recipe_name  | varchar(40)   | NO   | UNI | NULL    |                |
    | instructions | varchar(1000) | NO   |     | NULL    |                |
    +--------------+---------------+------+-----+---------+----------------+
Table of recipes and instructions how to make them. Instructions given as a free-text field. Recipe name is kept unique, to avoid ambiguity.

### ingredients

    +-----------------+-------------+------+-----+---------+----------------+
    | Field           | Type        | Null | Key | Default | Extra          |
    +-----------------+-------------+------+-----+---------+----------------+
    | id              | int(11)     | NO   | PRI | NULL    | auto_increment |
    | ingredient_name | varchar(40) | NO   | UNI | NULL    |                |
    +-----------------+-------------+------+-----+---------+----------------+
The list of ingredients used across all recipes. Ingredient name is kept unique.

### recipe_ingredients

    +---------------+-------------+------+-----+---------+-------+
    | Field         | Type        | Null | Key | Default | Extra |
    +---------------+-------------+------+-----+---------+-------+
    | recipe_id     | int(11)     | NO   | MUL | NULL    |       |
    | ingredient_id | int(11)     | NO   | MUL | NULL    |       |
    | quantity      | varchar(40) | NO   |     | NULL    |       |
    +---------------+-------------+------+-----+---------+-------+
Bridging table listing the ingredients used in each recipe, and their quantity. Quantity is also given as a free-text field e.g. "2 tbsp", "3 cups" etc... Could have kept quantity numeric and added a "units" field (or even a units table) - but am keeping this simple. 

## Recipes
The tables are populated with the following 3 recipes:

**1 .Chocolate Cake**

Ingredients: 2 tbsp, 5 cup flour, 3 eggs

Mix cocoa with flour; mix in the eggs; bake for 2 hours

**2. Tomato Soup**

Ingredients: 1kg tomatos, 1 onion, 1 carrot

Chop the onion; chop the carrot; boil them with the tomatos

**3. Scrambled Eggs**

Ingredients: 2 eggs, 2 bread, 1 knob butter

Melt butter in a pan; crack the eggs into it; mix the eggs; toast the bread


So, for instance, joining all the tables for Recipe 1 gives something like:

    +-----------+----------------+-----------------+----------+---------------------------------------------------------+
    | recipe_id | recipe_name    | ingredient_name | quantity | instructions                                            |
    +-----------+----------------+-----------------+----------+---------------------------------------------------------+
    |         1 | Chocolate Cake | cocoa powder    | 2 tbsp   | Mix cocoa with flour; mix ... |
    |         1 | Chocolate Cake | flour           | 5 cup    | Mix cocoa with flour; mix ... |
    |         1 | Chocolate Cake | eggs            | 3        | Mix cocoa with flour; mix ... |
    +-----------+----------------+-----------------+----------+---------------------------------------------------------+

## JSON
The API accepts and returns JSON. POST and PUT requests should have a JSON body - in a specified format I refer to as "recipe JSON" in the code. This object represents a recipe object - with a list of ingredients, the recipe's name and its instructions. For instance:

    {
    "ingredients": [
        {
        "ingredient": "bread", 
        "quantity": "2 pieces"
        }, 
        {
        "ingredient": "butter", 
        "quantity": "1 knob"
        }, 
        {
        "ingredient": "eggs", 
        "quantity": "2"
        }
    ], 
    "instructions": "Melt butter in a pan; crack the eggs into it; mix the eggs; toast the bread",
    "recipe": "Scrambled Eggs"
    }

There are checks in the code to ensure the bodies are in this format.

The GET requests for specific recipe_id's return a JSON object in almost the same format - except it also includes the recipe_id (whereas don't want to have to specify one in POST requests - it should be generated autmatically).