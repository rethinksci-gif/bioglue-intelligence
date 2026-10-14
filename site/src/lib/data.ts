import fs from 'node:fs';
import path from 'node:path';
import { load as yamlLoad } from 'js-yaml';

const ROOT = path.resolve(process.cwd(), '..');
const DATA = path.join(ROOT, 'data');
const read = (p: string) => fs.readFileSync(path.join(DATA, p), 'utf8');
const readYaml = <T>(p: string) => yamlLoad(read(p)) as T;

export const SITE_NAME = 'BIOGLUE Intelligence';
export const REPO = 'https://github.com/rethinksci-gif/bioglue-intelligence';
export const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');
export const url = (p: string) => `${BASE}/${p}`;

export interface Route {
  id: string; name: string; family: string; tagline: string; overview: string[]; chemistry: string[];
  structures: string[]; applications: string[]; incumbent: string; maturity: string;
  strengths: string[]; challenges: string[]; watch: string[]; refs: string[];
}
export interface Structure { id: string; name: string; smiles: string; role: string; routes: string[]; inchikey?: string }
export interface Reference { id: string; authors: string; year: number; title: string; journal: string; doi?: string; url?: string; kind: string; routes: string[] }
export interface Challenge { id: string; title: string; summary: string; detail?: string[]; ask: string; routes: string[] }
export interface Fact { field: string; label: string; value: string; quote: string; source: string; locator: string; [k: string]: string }
export interface Item {
  id: string; routes: string[]; route_note?: string; headline: string; organization: string; date: string;
  evidence_type: string; confidence: string; what_changed: string; why_it_matters: string; limitation: string;
  next: string; uncertainty: string; facts: Fact[]; not_assessed: string[];
}
export interface Hold { id: string; routes: string[]; title: string; date: string | null; doi: string; reason: string }
export interface Source { id: string; title: string; url: string; doi: string | null; published: string | null; version_date: string | null; kind: string; access: string }
export interface Quarter { quarter: string; status: string; version: number; review: string; items: Item[]; holds: Hold[]; sources: Source[] }
export interface Candidate {
  id: string; kind: string; title: string; venue: string; authors: string; date: string; date_precision?: string; url: string;
  route: string; relevance: number; signal: string; application: string; summary: string; quote: string;
  flags: string[]; shown: boolean;
}
export interface CandidateFile { quarter: string; window: [string, string]; scanned_through: string; updated: string; model: string; llm_calls: number; note: string; candidates: Candidate[] }

export const routes = readYaml<Route[]>('routes.yaml');
export const structures = readYaml<Structure[]>('structures.yaml');
export const references = readYaml<Reference[]>('references.yaml');
export const challenges = readYaml<Challenge[]>('challenges.yaml');
export interface Newsletter { id: string; title: string; window: [string, string]; cutoff: string; status: string; pdf: string; web: string; cover: string; summary: string;
  leads: { n: number; headline: string; route: string; doi: string; note: string }[]; watch: { label: string; text: string }[] }
const nlDir = path.join(DATA, 'newsletter');
const fmtD = (d: unknown) => (d instanceof Date ? d.toISOString().slice(0, 10) : String(d));
export const newsletters: Newsletter[] = (fs.existsSync(nlDir) ? fs.readdirSync(nlDir).filter((f) => f.endsWith('.yaml')).sort().reverse() : [])
  .map((f) => readYaml<any>(`newsletter/${f}`))
  .map((n) => ({ ...n, id: String(n.id), cutoff: fmtD(n.cutoff), window: [fmtD(n.window[0]), fmtD(n.window[1])] }));
export const glossary = readYaml<{ term: string; kind: string; text: string }[]>('glossary.yaml');

const jsonDir = <T>(dir: string): T[] => {
  const d = path.join(DATA, dir);
  if (!fs.existsSync(d)) return [];
  return fs.readdirSync(d).filter((f) => f.endsWith('.json')).sort().map((f) => JSON.parse(fs.readFileSync(path.join(d, f), 'utf8')) as T);
};
export const quarters = jsonDir<Quarter>('quarters');
export const candidates = jsonDir<CandidateFile>('candidates');

/** The four tracked quarters, newest first. */
export const QUARTERS = ['2026-Q4', '2026-Q3', '2026-Q2', '2026-Q1'];
export function windowOf(q: string): [string, string] {
  const y = +q.slice(0, 4), n = +q.slice(-1);
  const months = [[12, 2], [3, 5], [6, 8], [9, 11]][n - 1];
  const sy = n === 1 ? y - 1 : y;
  const last = new Date(Date.UTC(y, months[1], 0)).getUTCDate();
  return [`${sy}-${String(months[0]).padStart(2, '0')}-01`, `${y}-${String(months[1]).padStart(2, '0')}-${last}`];
}
export function quarterLabel(q: string) {
  const [s, e] = windowOf(q);
  const f = (d: string) => new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
  return `${f(s)} – ${f(e)}`;
}
export const fmtDate = (d: string | null) =>
  d ? new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }) : 'Date not established';

export const routeById = (id: string) => routes.find((r) => r.id === id);
export const refById = (id: string) => references.find((r) => r.id === id);
export const structureSvg = (id: string) => {
  const p = path.join(process.cwd(), 'src', 'generated', 'structures', `${id}.svg`);
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
};
export const quarterData = (q: string) => quarters.find((x) => x.quarter === q);
export const candidateData = (q: string) => candidates.find((x) => x.quarter === q);
export const shownCandidates = (q: string, route?: string) =>
  (candidateData(q)?.candidates ?? []).filter((c) => c.shown && (!route || c.route === route));
export const evidenceFor = (q: string, route: string) => (quarterData(q)?.items ?? []).filter((i) => i.routes.includes(route));
export const holdsFor = (q: string, route: string) => (quarterData(q)?.holds ?? []).filter((h) => h.routes.includes(route));
export const refLink = (r: Reference) => (r.doi ? `https://doi.org/${r.doi}` : r.url ?? '#');
export const refRoutes = (id: string) => references.filter((r) => r.routes.includes(id) || r.routes.includes('general'));
