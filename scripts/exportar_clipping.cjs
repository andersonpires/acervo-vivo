/**
 * Exporta o clipping do site do Iteva para scripts/clipping/banco.json.
 *
 * Uso:
 *   node scripts/exportar_clipping.cjs
 *   python -I scripts/extrair_clipping.py      (passo seguinte)
 *
 * Lê direto do banco do site novo (só leitura). O banco guarda título,
 * data, um resumo escrito pelo Iteva, o link da matéria original e uma
 * imagem; o texto da imprensa não está lá. Quem busca o original e grava
 * acervo/clipping é o extrair_clipping.py.
 *
 * Depende do projeto do site, que fica ao lado deste:
 *   SITE_ITEVA   pasta do site (padrão: ../site_iteva)
 *
 * Re-executável: regrava o JSON inteiro.
 */
const fs = require('fs')
const path = require('path')

const RAIZ = path.resolve(__dirname, '..')
const SITE = path.resolve(process.env.SITE_ITEVA || path.join(RAIZ, '..', 'site_iteva'))
const SAIDA = path.join(RAIZ, 'scripts', 'clipping', 'banco.json')
const BASE_URL = 'https://www.iteva.org.br/clipping/'

process.loadEnvFile(path.join(SITE, '.env'))
const { Client } = require(path.join(SITE, 'site_novo', 'node_modules', 'pg'))

/** Converte o JSON do editor Lexical em texto corrido, um parágrafo por linha. */
function texto(no) {
  if (!no) return ''
  if (no.type === 'text') return no.text || ''
  if (no.type === 'linebreak') return '\n'
  const filhos = (no.children || []).map(texto).join('')
  if (no.type === 'root') return (no.children || []).map(texto).map((b) => b.trim()).filter(Boolean).join('\n\n')
  return filhos
}

;(async () => {
  const c = new Client({ connectionString: process.env.DATABASE_URI })
  await c.connect()
  await c.query('SET default_transaction_read_only = on')
  const { rows } = await c.query(
    `select c.id, c.titulo, c.slug, c.data_publicacao, c.veiculo, c.descricao,
            c.link_materia, c.texto_link, c.id_legado, i.filename as imagem
       from clippings c left join imagens i on i.id = c.imagem_id
      where c.situacao = 'publicado' order by c.data_publicacao, c.id`,
  )
  await c.end()

  const registros = rows.map((r) => ({
    id_site: r.id,
    id_legado: r.id_legado == null ? null : Number(r.id_legado),
    titulo: r.titulo,
    data: new Date(r.data_publicacao).toISOString().slice(0, 10),
    url_site: BASE_URL + encodeURI(r.slug),
    slug: r.slug,
    veiculo: r.veiculo || '',
    resumo: texto(r.descricao?.root),
    link_materia: r.link_materia || '',
    texto_link: r.texto_link || '',
    imagem: r.imagem || '',
  }))

  fs.mkdirSync(path.dirname(SAIDA), { recursive: true })
  fs.writeFileSync(SAIDA, JSON.stringify(registros, null, 1) + '\n', 'utf8')
  console.log(`${registros.length} matérias gravadas em ${path.relative(RAIZ, SAIDA)}`)
})()
