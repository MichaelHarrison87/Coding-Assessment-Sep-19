from flask import Flask, jsonify, request
from flask_restful import Resource, Api, abort
import MySQLdb

app = Flask(__name__)
api = Api(app)
db = MySQLdb.connect(passwd="dummy", db="task_2")

def add_recipe(recipe_json):
    """
    Utility function to add a recipe (as specified in the recipe_json) to the database.
    Need this functionality in both the POST request to create new recipes, and 
    the PUT request, to help overwrite an existing recipe
    """
            
    try:
        ingredients_list = recipe_json["ingredients"] 
        instructions = recipe_json["instructions"]
        recipe_name = recipe_json["recipe_name"]
    except TypeError as e:
        return abort(400, message=f'400 Bad Request Error! Must provide a recipe JSON object!')
    except KeyError as e:
        return abort(400, message=f'400 Bad Request Error! Recipe must include field \'{e.args[0]}\'!')
        
    # Ingredients must be a list, even if only 1 item
    if not isinstance(ingredients_list, list):
        ingredients_list = [ingredients_list]
        
    # Now update the database - first the recipes (exception below catches recipe_names already in the recipes table)        
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO recipes (recipe_name, instructions) VALUES
                            (%s, %s);""", (recipe_name, instructions))
    except MySQLdb.IntegrityError as e:
        cur.close()
        return abort(400, message=f'400 Bad Request Error! MySQL Error: {repr(e)}')
    
    # Get the new recipe_id - need it when updating the recipe_ingredients table
    cur.execute("""SELECT id from recipes WHERE recipe_name = %s""", (recipe_name,))
    recipe_id = cur.fetchone()[0]
    
    # Now update the ingredients
    ingredients_sql = [(d['ingredient_name'].lower()) for d in ingredients_list]

    # Note: IGNORE below skips the insert if ingredient_name is already in the ingredients table
    cur.executemany("""INSERT IGNORE INTO ingredients (ingredient_name) VALUES
                        (%s);""", ingredients_sql)
    
    # Get the ingredient_id's:
    ingredient_ids_dict = {}
    for ingredient in ingredients_sql:
        cur.execute("""SELECT id from ingredients WHERE ingredient_name = %s;""", (ingredient,))
        ingredient_id = cur.fetchone()[0]
        ingredient_ids_dict[ingredient] = ingredient_id
    
    # Finally, we can update the recipe_ingredients table
    recipe_ingredients_sql = []
    for d in ingredients_list:
        name = d['ingredient_name']
        quantity = d['quantity']
        ingredient_id = ingredient_ids_dict[name] 
        recipe_ingredients_sql.append((recipe_id, ingredient_id, quantity))

    cur.executemany("""INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES
                (%s, %s, %s);""", recipe_ingredients_sql)
    
    cur.close()
    db.commit()
    return 201


class Root(Resource):
    """
    GET request at root URI "/" returns a list of available recipes, and a list of ingredients;
    POST takes a recipe JSON object and adds the recipe to the database (fails if there's already a recipe of the same name)
    """
    def get(self):
        cur = db.cursor()
        
        # Get recipes
        cur.execute("""SELECT id, recipe_name from recipes""")
        recipes = cur.fetchall()
        recipes_list = [{'recipe_id': int(recipe[0]), 'recipe_name': recipe[1]} for recipe in recipes]
        
        # Get ingredients
        cur.execute("""SELECT id, ingredient_name from ingredients""")
        ingredients = cur.fetchall()
        ingredients_list = [{'ingredient_id': int(ingredient[0]), 'recipe_name': ingredient[1]} 
                            for ingredient in ingredients]        
        
        cur.close()
        return jsonify({'recipes': recipes_list, 'ingredients': ingredients_list})

    def post(self):
        """
        The request body should be a recipe JSON object - which we assume follows the same format as the objects 
        returned by the GET method of Recipes below (see also the README). With the exception that the POST body doesn't 
        provide a recipe_id, as this'll be created automatically by the MySQL database.
        """
        recipe_json = request.get_json()
        return_status = add_recipe(recipe_json)
        return return_status


class Recipes(Resource):
    """
    GET: At URI "/recipe/<recipe_id>" we get recipe, instructions, ingredients etc
    DELETE: deletes the given recipe
    PUT: overwrites the given recipe - takes a full recipe JSON object as its body 
    """
    def get(self, recipe_id):
        recipes_dict = {"recipe_id": recipe_id}
        cur = db.cursor()
        
        # Get recipe name and instructions
        cur.execute("""SELECT recipe_name, instructions 
                        FROM recipes 
                        WHERE id = %s""", (recipe_id,))
        
        # Return 404 error if desired recipe_id doesn't exist
        try:
            recipe_name, instructions = cur.fetchone()
        except TypeError:
            cur.close()
            return abort(404, message=f'404 Not Found Error! recipe_id {recipe_id} does not exist!')
        
        # Get list of ingredients and quantities for the given recipe
        cur.execute("""SELECT ingredients.ingredient_name, quantity 
                        FROM recipe_ingredients
                        INNER JOIN ingredients 
                        ON recipe_ingredients.ingredient_id = ingredients.id 
                        WHERE recipe_id = %s""", (recipe_id,))
        ingredients = cur.fetchall()
        
        cur.close()
        
        # Ingregients list is a list of dicts containing name & quantity for each ingredient
        ingredients_list = [{'ingredient_name': ingredient[0], 'quantity': ingredient[1]} 
                            for ingredient in ingredients]
        
        recipes_dict['recipe_name'] = recipe_name
        recipes_dict['instructions'] = instructions
        recipes_dict['ingredients'] = ingredients_list
        return jsonify(recipes_dict)        

    def delete(self, recipe_id):
        cur = db.cursor()
        
        # Check recipe_id is in the database, exit if not
        cur.execute("""SELECT id from recipes WHERE id = %s;""", (recipe_id,))
        try:
            rec_id = cur.fetchone()[0]
        except TypeError:
            cur.close()
            return abort(404, message=f'404 Not Found Error! recipe_id {recipe_id} does not exist!')

        # First get list of ingredient_id's so can remove them from the ingredients table if no other recipe uses them 
        cur.execute("""SELECT ingredient_id FROM recipe_ingredients WHERE recipe_id = %s;""", (recipe_id,))
        ingredient_id_list = cur.fetchall()

        # Then delete the recipe 
        cur.execute("""DELETE FROM recipes WHERE id = %s;""", (recipe_id,))
        cur.execute("""DELETE FROM recipe_ingredients WHERE recipe_id = %s;""", (recipe_id,))

        # Now iterate over the ingredients and check if they're still in the recipe_ingredients table
        missing_ingredient_ids = []
        for ingredient in ingredient_id_list:
            cur.execute("""SELECT ingredient_id FROM recipe_ingredients WHERE ingredient_id = %s;""", ingredient)
            try:
                ing_id = cur.fetchone()[0]
            except TypeError:
                missing_ingredient_ids.append(ingredient)
        
        # Delete these "orphaned" ingredients:
        cur.executemany("""DELETE FROM ingredients WHERE id = %s;""", missing_ingredient_ids)

        cur.close()
        db.commit()
        return 204

    def put(self, recipe_id):
        recipe_json = request.get_json()

        # Ensure recipe_json has required fields:
        try:
            ingredients_list = recipe_json["ingredients"] 
            instructions = recipe_json["instructions"]
            recipe_name = recipe_json["recipe_name"]
        except TypeError as e:
            return abort(400, message=f'400 Bad Request Error! Must provide a recipe JSON object!')
        except KeyError as e:
            return abort(400, message=f'400 Bad Request Error! Recipe must include field \'{e.args[0]}\'!')
            
        # Then check recipe_id is in the database, exit if not
        cur = db.cursor()
        cur.execute("""SELECT id from recipes WHERE id = %s;""", (recipe_id,))
        
        try:
            rec_id = cur.fetchone()[0]
        except TypeError:
            cur.close()
            return abort(404, message=f'404 Not Found Error! recipe_id {recipe_id} does not exist!')
        
        # If all's good, delete then re-create the recipe in the database:
        self.delete(recipe_id)
        return_status = add_recipe(recipe_json)
        return return_status

class Ingredients(Resource):
    """
    GET: At URI "/ingredient/<ingredient_id>" get list of recipes containing specified ingredient
    """
    def get(self, ingredient_id):
        cur = db.cursor()
        
        # Get ingredient name, exit if ingredient_id not present
        cur.execute("""SELECT ingredient_name 
                        FROM ingredients
                        WHERE id = %s""", (ingredient_id,))        
        ingredient_name = cur.fetchone()[0]
        if ingredient_name is None:
            cur.close()
            return abort(404, message=f'404 Not Found Error! ingredient_id {ingredient_id} does not exist!')
        
        # Now get the recipe_id's
        cur.execute("""SELECT recipe_id 
                        FROM recipe_ingredients
                        WHERE ingredient_id = %s
                        GROUP BY recipe_id""", (ingredient_id,))
        recipe_ids = cur.fetchall()
        print(recipe_ids)
        
        # And their names - want to return a list of dicts (each with the id and recipe name)
        recipe_names = []
        for recipe_id in recipe_ids:
            recipe_dict = {}
            cur.execute("""SELECT recipe_name FROM recipes WHERE id = %s;""", recipe_id)
            recipe = cur.fetchone()[0]
            
            recipe_dict["recipe_id"] = recipe_id[0]
            recipe_dict["recipe_name"] = recipe
            recipe_names.append(recipe_dict)
            

        cur.close()
        response = {'ingredient_id': ingredient_id, 
                    'ingredient_name': ingredient_name, 
                    'recipes': recipe_names}
        return jsonify(response)

        
api.add_resource(Root, '/')
api.add_resource(Recipes, '/recipe/<int:recipe_id>')
api.add_resource(Ingredients, '/ingredient/<int:ingredient_id>')


if __name__ == '__main__':
    app.run(debug=True)
    db.close()