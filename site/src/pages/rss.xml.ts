import { SITE_NAME, QUARTERS, shownCandidates, quarterData, routeById } from '../lib/data';
const site = 'https://rethinksci-gif.github.io/bioglue-intelligence/';
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export function GET() {
  const items: { title: string; link: string; date: string; desc: string }[] = [];
  for (const q of QUARTERS) {
    for (const it of quarterData(q)?.items ?? []) items.push({ title: `[checked] ${it.headline}`, link: `${site}tracker/${q}/#${it.id}`, date: it.date, desc: it.what_changed });
    for (const c of shownCandidates(q)) items.push({ title: `[lead · ${routeById(c.route)?.name}] ${c.title}`, link: c.url, date: c.date, desc: c.summary });
  }
  items.sort((a, b) => b.date.localeCompare(a.date));
  const xml = `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>${SITE_NAME}</title><link>${site}</link><description>Bio-based wood adhesive developments: evidence-checked items and machine-triaged leads.</description>${items.slice(0, 100).map((i) => `<item><title>${esc(i.title)}</title><link>${esc(i.link)}</link><guid>${esc(i.link)}</guid><pubDate>${new Date(i.date + 'T00:00:00Z').toUTCString()}</pubDate><description>${esc(i.desc)}</description></item>`).join('')}</channel></rss>`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
}
