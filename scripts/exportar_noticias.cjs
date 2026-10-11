/**
 * Exporta as notícias publicadas do site do Iteva para acervo/noticias.
 *
 * Uso:
 *   node scripts/exportar_noticias.cjs
 *
 * Lê direto do banco do site novo (só leitura, nenhum UPDATE), em vez de
 * raspar as páginas: o texto sai exato e a data é a de publicação gravada.
 * Rascunhos ficam de fora, porque o público não os vê.
 *
 * Depende do projeto do site, que fica ao lado deste:
 *   SITE_ITEVA   pasta do site (padrão: ../site_iteva)
 * O driver `pg` vem de SITE_ITEVA/site_novo/node_modules e a conexão,
 * de DATABASE_URI em SITE_ITEVA/.env.
 *
 * Re-executável: apaga e regrava os .md da pasta de saída.
 */
const fs = require('fs')
const path = require('path')

const RAIZ = path.resolve(__dirname, '..')
const SITE = path.resolve(process.env.SITE_ITEVA || path.join(RAIZ, '..', 'site_iteva'))
const SAIDA = path.join(RAIZ, 'acervo', 'noticias')
const BASE_URL = 'https://www.iteva.org.br/noticia/'

process.loadEnvFile(path.join(SITE, '.env'))
const { Client } = require(path.join(SITE, 'site_novo', 'node_modules', 'pg'))

/** Converte o JSON do editor Lexical em Markdown simples. */
function markdown(no) {
  if (!no) return ''
  const filhos = () => (no.children || []).map(markdown).join('')
  switch (no.type) {
    case 'root':
      return (no.children || []).map(markdown).filter((b) => b.trim()).join('\n\n')
    case 'paragraph':
      return filhos().trim()
    case 'heading':
      return '#'.repeat(Math.min(6, Number(no.tag.slice(1)) + 1)) + ' ' + filhos().trim()
    case 'quote':
      return '> ' + filhos().trim()
    case 'list':
      return (no.children || [])
        .map((li, i) => (no.listType === 'number' ? `${i + 1}. ` : '- ') + markdown(li).trim())
        .join('\n')
    case 'listitem':
      return filhos()
    case 'text': {
      let t = no.text || ''
      // Formato Lexical: 1 negrito, 2 itálico.
      if (t.trim() && no.format & 1) t = `**${t}**`
      if (t.trim() && no.format & 2) t = `*${t}*`
      return t
    }
    case 'linebreak':
      return '\n'
    case 'link':
    case 'autolink': {
      const url = no.fields?.url || no.url || ''
      return url ? `[${filhos()}](${url})` : filhos()
    }
    case 'upload':
      return '(imagem)'
    default:
      return filhos()
  }
}

function data(d) {
  return new Date(d).toISOString().slice(0, 10)
}

function yamlTexto(s) {
  return JSON.stringify(s ?? '')
}

;(async () => {
  const c = new Client({ connectionString: process.env.DATABASE_URI })
  await c.connect()
  const { rows } = await c.query(
    `select id, titulo, slug, subtitulo, data_publicacao, resumo, conteudo, id_legado
       from noticias where situacao = 'publicado' order by data_publicacao, id`,
  )
  await c.end()

  fs.mkdirSync(SAIDA, { recursive: true })
  for (const f of fs.readdirSync(SAIDA)) if (f.endsWith('.md')) fs.unlinkSync(path.join(SAIDA, f))

  for (const n of rows) {
    const url = BASE_URL + encodeURI(n.slug)
    const corpo = markdown(n.conteudo?.root)
    const linhas = [
      '---',
      `titulo: ${yamlTexto(n.titulo)}`,
      `subtitulo: ${yamlTexto(n.subtitulo)}`,
      `data: ${data(n.data_publicacao)}`,
      `url: ${url}`,
      `resumo: ${yamlTexto(n.resumo)}`,
      `id_site: ${n.id}`,
      `id_legado: ${n.id_legado ?? ''}`,
      '---',
      '',
      `# ${n.titulo}`,
      '',
      corpo || '[FALTA: notícia sem texto no site]',
      '',
    ]
    const arquivo = `${data(n.data_publicacao)}-${n.slug}.md`.replace(/[^\w.-]/g, '_')
    fs.writeFileSync(path.join(SAIDA, arquivo), linhas.join('\n'), 'utf8')
  }
  console.log(`${rows.length} notícias gravadas em ${path.relative(RAIZ, SAIDA)}`)
})()
