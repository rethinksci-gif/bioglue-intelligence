import { references } from '../lib/data';
export function GET() {
  const esc = (s: string) => s.replace(/[{}]/g, '');
  const body = references.map((r) => {
    const type = r.kind === 'regulation' ? 'misc' : 'article';
    const fields = [`title = {${esc(r.title)}}`, `author = {${esc(r.authors.replace(/, et al\.$/, ' and others').replace(/\., /g, '. and '))}}`, `year = {${r.year}}`, `journal = {${esc(r.journal)}}`];
    if (r.doi) fields.push(`doi = {${r.doi}}`);
    if (r.url) fields.push(`url = {${r.url}}`);
    return `@${type}{${r.id},\n  ${fields.join(',\n  ')}\n}`;
  }).join('\n\n');
  return new Response(body + '\n', { headers: { 'Content-Type': 'application/x-bibtex; charset=utf-8' } });
}
