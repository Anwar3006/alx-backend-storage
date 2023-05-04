DELIMITER $$
CREATE TRIGGER add_insert
AFTER INSERT 
ON table_2 FOR EACH ROW   --after you insert any value in table 2
BEGIN
    UPDATE table_1
        SET table_1_attribute = table_1_attribute +/- NEW.table_2_attribute;
        --eg:    quantity     =      quantity      -        new.number
        WHERE table_1_attribute = NEW.corresponding_table_2_attribute
        --eg:        name       =            new.item_name
END $$
DELIMITER;




CREATE TABLE IF NOT EXISTS items (
    name VARCHAR(255) NOT NULL,
    quantity int NOT NULL DEFAULT 10
);

CREATE TABLE IF NOT EXISTS orders (
    item_name VARCHAR(255) NOT NULL,
    number int NOT NULL
);
