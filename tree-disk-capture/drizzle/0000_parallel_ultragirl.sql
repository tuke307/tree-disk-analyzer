CREATE TABLE `analysis` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`predicted_age` integer,
	`segmentation_id` integer,
	`pith_id` integer,
	`rings_id` integer,
	FOREIGN KEY (`segmentation_id`) REFERENCES `segmentation`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`pith_id`) REFERENCES `pith`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`rings_id`) REFERENCES `rings`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `capture` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`image_base64` text NOT NULL,
	`timestamp` text NOT NULL,
	`width` integer NOT NULL,
	`height` integer NOT NULL,
	`analysis_id` integer,
	FOREIGN KEY (`analysis_id`) REFERENCES `analysis`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `pith` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`x` integer NOT NULL,
	`y` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `rings` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`image_base64` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `segmentation` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`image_base64` text NOT NULL
);
