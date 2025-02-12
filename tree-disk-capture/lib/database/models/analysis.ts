import { Segmentation, Pith, Rings } from '@/lib/database/models';

export class Analysis {
  predictedAge?: number;

  segmentation!: Segmentation | undefined;

  pith!: Pith | undefined;

  rings!: Rings | undefined;
}