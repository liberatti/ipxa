export interface Feed {
  _id?: number;
  name: string;
  slug: string;
  provider: string;
  restricted: boolean;
  type: 'reputation' | 'bypass';
  source?: string;
  data?: string[];
  description: string;
  format: 'embedded' | 'cdir_text' | 'cdir_gz';
  update_interval: 'hourly' | 'daily';
  updated_on?: string;
  risk_score: number;
}
