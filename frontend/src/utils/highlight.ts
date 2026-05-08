export function highlightText(text: string, query: string): string {
  if (!query.trim()) return escapeHtml(text)

  const escaped = query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const terms = escaped.split(/\s+/).filter(Boolean)

  let result = escapeHtml(text)
  for (const term of terms) {
    const regex = new RegExp(`(${term})`, 'gi')
    result = result.replace(regex, '<mark>$1</mark>')
  }
  return result
}

function escapeHtml(raw: string): string {
  return raw
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}
