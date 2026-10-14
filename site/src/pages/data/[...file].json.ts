import { routes, structures, challenges, references, quarters, candidates } from '../../lib/data';
const strip = (c: any) => { const { abstract, query, seed_routes, ...rest } = c; return rest; };
const files: Record<string, unknown> = {
  routes, structures, challenges, references,
  ...Object.fromEntries(quarters.map((q) => [`quarters/${q.quarter}`, q])),
  ...Object.fromEntries(candidates.map((c) => [`candidates/${c.quarter}`, { ...c, candidates: c.candidates.filter((x) => x.shown).map(strip) }])),
};
export function getStaticPaths() { return Object.keys(files).map((file) => ({ params: { file } })); }
export function GET({ params }: { params: { file: string } }) {
  return new Response(JSON.stringify(files[params.file], null, 2), { headers: { 'Content-Type': 'application/json' } });
}
