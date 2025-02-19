PRAGMA foreign_keys=OFF;--> statement-breakpoint
CREATE TABLE `__new_capture` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`image_base64` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`width` integer NOT NULL,
	`height` integer NOT NULL,
	`analysis_id` integer,
	FOREIGN KEY (`analysis_id`) REFERENCES `analysis`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
INSERT INTO `__new_capture`("id", "title", "image_base64", "created_at", "updated_at", "width", "height", "analysis_id") SELECT "id", "title", "image_base64", "created_at", "updated_at", "width", "height", "analysis_id" FROM `capture`;--> statement-breakpoint
DROP TABLE `capture`;--> statement-breakpoint
ALTER TABLE `__new_capture` RENAME TO `capture`;--> statement-breakpoint
PRAGMA foreign_keys=ON;--> statement-breakpoint
ALTER TABLE `analysis` ADD `created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `analysis` ADD `updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `pith` ADD `created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `pith` ADD `updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `rings` ADD `created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `rings` ADD `updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `segmentation` ADD `created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;--> statement-breakpoint
ALTER TABLE `segmentation` ADD `updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL;