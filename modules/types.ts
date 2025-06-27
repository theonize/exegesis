export interface TextEntry {
  id: string;
  content: string;
  meta?: Record<string, any>;
}

export type NoteType =
  | "historical"
  | "cultural"
  | "literary"
  | "application";

export interface NoteEntry {
  id: string;
  ref: string;
  type: NoteType;
  content: string;
  meta?: Record<string, any>;
}

export interface Database {
  texts: TextEntry[];
  notes: NoteEntry[];
}
