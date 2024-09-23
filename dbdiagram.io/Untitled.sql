CREATE TABLE `users` (
  `user_id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM ('patient', 'doctor') NOT NULL
);

CREATE TABLE `patients` (
  `patient_id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `name` VARCHAR(25),
  `address` VARCHAR(255),
  `phone_number` VARCHAR(20)
);

CREATE TABLE `doctors` (
  `doctor_id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `hospital_id` INT NOT NULL,
  `specialization` VARCHAR(255),
  `availability_schedule` JSON
);

CREATE TABLE `medical_records` (
  `record_id` INT PRIMARY KEY AUTO_INCREMENT,
  `patient_id` INT NOT NULL,
  `doctor_id` INT NOT NULL,
  `date_created` DATETIME DEFAULT (CURRENT_TIMESTAMP),
  `description` TEXT,
  `diagnosis` VARCHAR(255),
  `treatment_plan` TEXT
);

CREATE TABLE `appointments` (
  `appointment_id` INT PRIMARY KEY AUTO_INCREMENT,
  `patient_id` INT NOT NULL,
  `doctor_id` INT NOT NULL,
  `hospital_id` INT UNIQUE NOT NULL,
  `appointment_date` DATETIME NOT NULL,
  `appointment_time` TIME NOT NULL,
  `symtomps` VARCHAR(255),
  `type` ENUM ('pribadi', 'asuransi') NOT NULL,
  `status` ENUM ('pending', 'confirmed', 'completed', 'cancelled') NOT NULL
);

CREATE TABLE `otp_codes` (
  `otp_id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `code` VARCHAR(6) NOT NULL,
  `created_at` DATETIME DEFAULT (CURRENT_TIMESTAMP),
  `expires_at` DATETIME NOT NULL
);

CREATE TABLE `hospitals` (
  `hospital_id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAT(20) NOT NULL,
  `address` VARCHAR(255),
  `phone_number` VARCHAR(15)
);

ALTER TABLE `users` ADD FOREIGN KEY (`user_id`) REFERENCES `patients` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `doctors` ADD FOREIGN KEY (`hospital_id`) REFERENCES `hospitals` (`hospital_id`) ON DELETE CASCADE;

ALTER TABLE `doctors` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `medical_records` ADD FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE;

ALTER TABLE `medical_records` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE;

ALTER TABLE `appointments` ADD FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE;

ALTER TABLE `appointments` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE;

ALTER TABLE `otp_codes` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `hospitals` ADD FOREIGN KEY (`hospital_id`) REFERENCES `appointments` (`hospital_id`) ON DELETE CASCADE;
