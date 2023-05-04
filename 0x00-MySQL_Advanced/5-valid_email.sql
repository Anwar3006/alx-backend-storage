-- SQL script that creates a trigger that resets the attribute valid_email only when the email has been changed
DELIMITER $$

CREATE TRIGGER reset_valid_email
AFTER INSERT
ON users FOR EACH ROW
BEGIN
    UPDATE valid_email
        SET valid_email = 1
        WHERE email = NEW.email
END $$
DELIMITER;
