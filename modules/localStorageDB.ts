import { Database, TextEntry, NoteEntry } from './types';
import { globToRegex } from './utils';

/**
 * Simple wrapper around browser localStorage for CRUD operations
 * following the schema defined in AGENTS.md.
 */
export class LocalStorageDB {
  private storageKey: string;

  constructor(storageKey = 'exegesis-db') {
    this.storageKey = storageKey;
    if (!this.getRaw()) {
      this.save({ texts: [], notes: [] });
    }
  }

  /** Load raw string from localStorage. */
  private getRaw(): string | null {
    if (typeof localStorage === 'undefined') return null;
    return localStorage.getItem(this.storageKey);
  }

  /** Persist database object to localStorage. */
  private save(data: Database): void {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(this.storageKey, JSON.stringify(data));
  }

  /** Retrieve database object from localStorage. */
  private load(): Database {
    if (typeof localStorage === 'undefined') return { texts: [], notes: [] };
    const raw = this.getRaw();
    return raw ? (JSON.parse(raw) as Database) : { texts: [], notes: [] };
  }

  /* --------------------------- TextEntry CRUD --------------------------- */

  createText(entry: TextEntry): void {
    const db = this.load();
    db.texts.push(entry);
    this.save(db);
  }

  readText(id: string): TextEntry | undefined {
    return this.load().texts.find((t) => t.id === id);
  }

  updateText(entry: TextEntry): void {
    const db = this.load();
    const idx = db.texts.findIndex((t) => t.id === entry.id);
    if (idx !== -1) {
      db.texts[idx] = entry;
      this.save(db);
    }
  }

  deleteText(id: string): void {
    const db = this.load();
    db.texts = db.texts.filter((t) => t.id !== id);
    this.save(db);
  }

  listTexts(): TextEntry[] {
    return this.load().texts;
  }

  /* --------------------------- NoteEntry CRUD --------------------------- */

  createNote(entry: NoteEntry): void {
    const db = this.load();
    db.notes.push(entry);
    this.save(db);
  }

  readNote(id: string): NoteEntry | undefined {
    return this.load().notes.find((n) => n.id === id);
  }

  updateNote(entry: NoteEntry): void {
    const db = this.load();
    const idx = db.notes.findIndex((n) => n.id === entry.id);
    if (idx !== -1) {
      db.notes[idx] = entry;
      this.save(db);
    }
  }

  deleteNote(id: string): void {
    const db = this.load();
    db.notes = db.notes.filter((n) => n.id !== id);
    this.save(db);
  }

  listNotes(): NoteEntry[] {
    return this.load().notes;
  }

  /* ------------------------------ Queries ------------------------------ */

  /**
   * Query TextEntry records using glob pattern on id.
   */
  queryTexts(pattern: string): TextEntry[] {
    const regex = globToRegex(pattern);
    return this.load().texts.filter((t) => regex.test(t.id));
  }

  /**
   * Query NoteEntry records using glob pattern on ref.
   */
  queryNotesByRef(pattern: string): NoteEntry[] {
    const regex = globToRegex(pattern);
    return this.load().notes.filter((n) => regex.test(n.ref));
  }

  /**
   * Query NoteEntry records using glob pattern on id.
   */
  queryNotesById(pattern: string): NoteEntry[] {
    const regex = globToRegex(pattern);
    return this.load().notes.filter((n) => regex.test(n.id));
  }
}
