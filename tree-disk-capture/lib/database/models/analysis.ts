import { Segmentation, Pith, Rings } from '@/lib/database/models';

export class Analysis {
  predictedAge?: number;

  segmentation!: Segmentation;

  pith!: Pith;

  ring!: Rings;
}