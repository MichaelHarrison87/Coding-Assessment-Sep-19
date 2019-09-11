-- Script to create and populate our recipe tables

USE task_2;

CREATE TABLE recipes (
    id INT NOT NULL AUTO_INCREMENT,
    recipe_name VARCHAR(40) NOT NULL,
    instructions VARCHAR(1000) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY (recipe_name)
);

ALTER TABLE recipes AUTO_INCREMENT=1;

INSERT INTO recipes (recipe_name, instructions) VALUES
    ('Chocolate Cake', 'Mix cocoa with flour; mix in the eggs; bake for 2 hours'),
    ('Tomato Soup', 'Chop the onion; chop the carrot; boil them with the tomatos'),
    ('Scrambled Eggs', 'Melt butter in a pan; crack the eggs into it; mix the eggs; toast the bread');


CREATE TABLE ingredients (
    id INT NOT NULL AUTO_INCREMENT,
    ingredient_name VARCHAR(40) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY (ingredient_name)
);

ALTER TABLE ingredients AUTO_INCREMENT=1;

INSERT INTO ingredients (ingredient_name) VALUES
    ('bread'),
    ('butter'),
    ('carrots'),
    ('cocoa powder'),
    ('eggs'),
    ('flour'),
    ('onions'),
    ('tomatos');


CREATE TABLE recipe_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity VARCHAR(40) NOT NULL,
    
    INDEX (recipe_id, ingredient_id),
    INDEX (ingredient_id),
    
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    
    FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id)
);

INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES
    (1, 4, '2 tbsp'),
    (1, 6, '5 cup'),
    (1, 5, '3'),
    (2, 8, '1 kg'),
    (2, 7, '1'),
    (2, 3, '1'),
    (3, 5, '2'),
    (3, 1, '2 pieces'),
    (3, 2, '1 knob');

