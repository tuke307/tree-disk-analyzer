import { Analysis } from '@/lib/database/models';

export class Capture {
  id!: number;

  title!: string;

  image_base64!: string;

  timestamp!: Date;

  width!: number;

  height!: number;

  analysis!: Analysis;
}
