-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema scheduler
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `scheduler` ;

-- -----------------------------------------------------
-- Schema scheduler
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `scheduler` DEFAULT CHARACTER SET utf8 ;
USE `scheduler` ;

-- -----------------------------------------------------
-- Table `scheduler`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scheduler`.`users` ;

CREATE TABLE IF NOT EXISTS `scheduler`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `scheduler`.`tasks`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `scheduler`.`tasks` ;

CREATE TABLE IF NOT EXISTS `scheduler`.`tasks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `users_id` INT NOT NULL,
  `task_name` VARCHAR(255) NULL,
  `location` VARCHAR(255) NULL,
  `start_time` TIME NULL,
  `end_time` TIME NULL,
  `attendees` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_tasks_users_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_tasks_users`
    FOREIGN KEY (`users_id`)
    REFERENCES `scheduler`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
