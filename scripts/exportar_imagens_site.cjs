/**
 * Exporta as imagens publicadas no site do Iteva para acervo/imagens.
 *
 * Uso:
 *   node scripts/exportar_imagens_site.cjs
 *
 * Lê o banco do site (só leitura) para saber onde cada imagem é usada:
 * capa, galeria e corpo das notícias publicadas; blocos das páginas e
 * dos projetos; banners e parceiros da home; convidados e parceiros dos
 * Painéis Temáticos. Ícones decorativos, miniaturas do clipping e capas
 * de publicações ficam de fora.
 *
 * Saída:
 *   acervo/imagens/arquivos/<id>.<ext>   arquivo original (fora do git)
 *   acervo/imagens/contexto/site.jsonl   uma linha por imagem, com os usos
 *
 * O arquivo vem do site publicado; se falhar, da cópia do site antigo
 * (site_legado/public/<origem_legado>). Re-executável: não baixa de novo
 * o que já está na pasta com o mesmo tamanho.
 *
 * Depende do projeto do site, que fica ao lado deste:
 *   SITE_ITEVA   pasta do site (padrão: ../site_iteva)
 */
const fs = require('fs')
const path = require('path')

const RAIZ = path.resolve(__dirname, '..')
const SITE = path.resolve(process.env.SITE_ITEVA || path.join(RAIZ, '..', 'site_iteva'))
const PASTA = path.join(RAIZ, 'acervo', 'imagens')
const ARQUIVOS = path.join(PASTA, 'arquivos')
const CONTEXTO = path.join(PASTA, 'contexto', 'site.jsonl')
const BASE = 'https://www.iteva.org.br'

process.loadEnvFile(path.join(SITE, '.env'))
const { Client } = require(path.join(SITE, 'site_novo', 'node_modules', 'pg'))

function data(d) {
  return new Date(d).toISOString().slice(0, 10)
}

/** Mesmo nome de arquivo que scripts/exportar_noticias.cjs grava. */
function arquivoNoticia(n) {
  return `acervo/noticias/${data(n.data_publicacao)}-${n.slug}.md`.replace(/[^\w./-]/g, '_')
}

/** Texto corrido de um nó Lexical. */
function texto(no) {
  if (!no) return ''
  if (no.type === 'text') return no.text || ''
  if (no.type === 'linebreak') return '\n'
  return (no.children || []).map(texto).join('')
}

/** Imagens no corpo da notícia, com o parágrafo anterior e o seguinte. */
function noCorpo(conteudo) {
  const blocos = conteudo?.root?.children || []
  const achadas = []
  blocos.forEach((b, i) => {
    if (b.type !== 'upload' || b.relationTo !== 'imagens') return
    const vizinho = (passo) => {
      for (let j = i + passo; j >= 0 && j < blocos.length; j += passo) {
        const t = texto(blocos[j]).trim()
        if (t) return t
      }
      return ''
    }
    achadas.push({ imagem: Number(b.value?.id ?? b.value), antes: vizinho(-1), depois: vizinho(1) })
  })
  return achadas
}

const pad = (n) => String(n).padStart(2, '0')

;(async () => {
  const c = new Client({ connectionString: process.env.DATABASE_URI })
  await c.connect()
  const q = async (sql) => (await c.query(sql)).rows

  const imagens = new Map()
  for (const i of await q(`select * from imagens`)) imagens.set(`imagens:${i.id}`, i)
  // Logos de parceiros ficam na coleção marca, não em imagens.
  for (const i of await q(`select * from marca`)) imagens.set(`marca:${i.id}`, { ...i, texto_alternativo: i.titulo })

  // Ordem dos usos: notícias por data, depois o site. A imagem recebe o
  // id do primeiro uso; os demais entram na lista de usos.
  const usos = []

  const noticias = await q(`select id, titulo, slug, subtitulo, data_publicacao, resumo, capa_id, conteudo
      from noticias where situacao = 'publicado' order by data_publicacao, id`)
  const galeria = await q(`select _parent_id, _order, imagem_id from noticias_galeria order by _parent_id, _order`)
  for (const n of noticias) {
    const base = `not-${data(n.data_publicacao)}-${n.id}`
    const ctx = {
      fonte: 'noticia',
      titulo: n.titulo,
      subtitulo: n.subtitulo || '',
      data: data(n.data_publicacao),
      url: `${BASE}/noticia/${encodeURI(n.slug)}`,
      arquivo_acervo: arquivoNoticia(n),
      resumo: n.resumo || '',
    }
    if (n.capa_id) usos.push({ imagem: n.capa_id, id: `${base}-capa`, ...ctx, posicao: 'capa' })
    noCorpo(n.conteudo).forEach((u, k) =>
      usos.push({ imagem: u.imagem, id: `${base}-c${k + 1}`, ...ctx, posicao: 'corpo', texto_antes: u.antes, texto_depois: u.depois }),
    )
    galeria
      .filter((g) => g._parent_id === n.id && g.imagem_id)
      .forEach((g, k) => usos.push({ imagem: g.imagem_id, id: `${base}-g${pad(k + 1)}`, ...ctx, posicao: `galeria ${k + 1}` }))
  }

  // Projetos: blocos de imagem, carrossel, seções com imagem, grade de logos.
  const projetos = new Map((await q(`select id, titulo, slug from projetos where situacao = 'publicado'`)).map((p) => [p.id, p]))
  const ctxProjeto = (p) => ({
    fonte: 'site',
    titulo: p.titulo,
    url: `${BASE}/projeto/${p.slug}`,
    arquivo_acervo: `acervo/site/projeto/${p.slug}.md`,
  })
  const blocoProjeto = async (sql, montar) => {
    for (const r of await q(sql)) {
      const p = projetos.get(r.projeto)
      if (p && r.imagem_id) usos.push({ imagem: r.imagem_id, ...ctxProjeto(p), ...montar(r, p) })
    }
  }
  await blocoProjeto(
    `select _parent_id projeto, _order, imagem_id, legenda from projetos_blocks_imagem order by _parent_id, _order`,
    (r, p) => ({ id: `site-${p.slug}-imagem${pad(r._order)}`, posicao: 'bloco de imagem', legenda: r.legenda || '' }),
  )
  await blocoProjeto(
    `select b._parent_id projeto, b.titulo bloco, f._order, f.imagem_id from projetos_blocks_carrossel_fotos f
       join projetos_blocks_carrossel b on b.id = f._parent_id order by b._parent_id, b._order, f._order`,
    (r, p) => ({ id: `site-${p.slug}-carrossel${pad(r._order)}`, posicao: `carrossel "${r.bloco || ''}"` }),
  )
  await blocoProjeto(
    `select b._parent_id projeto, s._order, s.imagem_id, s.titulo, s.texto from projetos_blocks_secoes_com_imagem_secoes s
       join projetos_blocks_secoes_com_imagem b on b.id = s._parent_id order by b._parent_id, b._order, s._order`,
    (r, p) => ({ id: `site-${p.slug}-secao${pad(r._order)}`, posicao: 'seção com imagem', secao_titulo: r.titulo || '', secao_texto: r.texto || '' }),
  )
  await blocoProjeto(
    `select b._parent_id projeto, b.titulo bloco, l._order, l.imagem_id, l.nome, l.url from projetos_blocks_grade_de_logos_itens l
       join projetos_blocks_grade_de_logos b on b.id = l._parent_id order by b._parent_id, b._order, l._order`,
    (r, p) => ({ id: `site-${p.slug}-logo${pad(r._order)}`, posicao: `grade de logos "${r.bloco || ''}"`, nome: r.nome || '', link: r.url || '' }),
  )

  // Páginas institucionais: blocos de imagem.
  for (const r of await q(`select p.slug, p.titulo, b._order, b.imagem_id, b.legenda from paginas_blocks_imagem b
      join paginas p on p.id = b._parent_id where p.situacao = 'publicado' order by p.slug, b._order`)) {
    usos.push({
      imagem: r.imagem_id,
      id: `site-${r.slug}-imagem${pad(r._order)}`,
      fonte: 'site',
      titulo: r.titulo,
      url: `${BASE}/p/${r.slug}`,
      arquivo_acervo: `acervo/site/institucional/${r.slug}.md`,
      posicao: 'bloco de imagem',
      legenda: r.legenda || '',
    })
  }

  // Home: banners e parceiros.
  const home = { fonte: 'site', titulo: 'Página inicial', url: `${BASE}/`, arquivo_acervo: 'acervo/site/home.md' }
  for (const b of await q(`select * from banners where situacao = 'publicado' order by ordem, id`)) {
    const ctx = { ...home, chamada: [b.chamada, b.destaque, b.complemento].filter(Boolean).join(' | '), titulo_banner: b.titulo || '', link: b.url || '' }
    if (b.imagem_id) usos.push({ imagem: b.imagem_id, id: `site-home-banner${pad(b.ordem ?? b.id)}`, ...ctx, posicao: 'banner' })
    if (b.imagem_texto_id) usos.push({ imagem: b.imagem_texto_id, id: `site-home-banner${pad(b.ordem ?? b.id)}-texto`, ...ctx, posicao: 'texto do banner' })
  }
  for (const r of await q(`select g.titulo grupo, g._order grupo_ordem, i._order, i.nome, i.logo_id, i.url from parceiros_grupos_itens i
      join parceiros_grupos g on g.id = i._parent_id order by g._order, i._order`)) {
    if (r.logo_id) usos.push({ imagem: r.logo_id, colecao: 'marca', id: `site-home-parceiros${r.grupo_ordem}-${pad(r._order)}`, ...home, posicao: `parceiros "${r.grupo || ''}"`, nome: r.nome || '', link: r.url || '' })
  }

  // Painéis Temáticos: convidados e parceiros.
  const paineis = { fonte: 'site', titulo: 'Painéis Temáticos', url: `${BASE}/paineis-tematicos`, arquivo_acervo: 'acervo/site/evento/paineis-tematicos.md' }
  for (const r of await q(`select _order, tema, nome, papel, bio, foto_id from paineis_tematicos_convidados order by _order`)) {
    if (r.foto_id) usos.push({ imagem: r.foto_id, id: `site-paineis-convidado${pad(r._order)}`, ...paineis, posicao: 'foto de convidado', tema: r.tema || '', nome: r.nome || '', papel: r.papel || '', bio: r.bio || '' })
  }
  for (const r of await q(`select _order, nome, grupo, logo_id from paineis_tematicos_parceiros order by _order`)) {
    if (r.logo_id) usos.push({ imagem: r.logo_id, colecao: 'marca', id: `site-paineis-parceiro${pad(r._order)}`, ...paineis, posicao: `parceiros "${r.grupo || ''}"`, nome: r.nome || '' })
  }
  await c.end()

  // Uma entrada por imagem, com todos os usos.
  const porImagem = new Map()
  for (const { imagem, colecao = 'imagens', id, ...uso } of usos) {
    const chave = `${colecao}:${imagem}`
    const i = imagens.get(chave)
    if (!i) {
      console.warn(`imagem ${imagem} citada em ${id} não existe no banco`)
      continue
    }
    if (!porImagem.has(chave)) {
      const ext = path.extname(i.filename).toLowerCase() || '.jpg'
      porImagem.set(chave, {
        id,
        arquivo: `arquivos/${id}${ext}`,
        id_site: `${colecao} ${i.id}`,
        url_arquivo: BASE + i.url,
        origem_legado: i.origem_legado || '',
        largura: Number(i.width),
        altura: Number(i.height),
        bytes: Number(i.filesize),
        texto_alternativo: i.texto_alternativo || '',
        legenda_site: i.legenda || '',
        credito_site: i.credito || '',
        usos: [],
      })
    }
    porImagem.get(chave).usos.push(uso)
  }

  fs.mkdirSync(ARQUIVOS, { recursive: true })
  fs.mkdirSync(path.dirname(CONTEXTO), { recursive: true })
  const lista = [...porImagem.values()]
  const antes = new Map()
  if (fs.existsSync(CONTEXTO))
    for (const linha of fs.readFileSync(CONTEXTO, 'utf8').split('\n').filter(Boolean)) {
      const e = JSON.parse(linha)
      antes.set(e.id, e.obtida_de)
    }
  let baixadas = 0, legado = 0, prontas = 0, falhas = 0
  const fila = [...lista]
  const trabalhador = async () => {
    for (let e = fila.shift(); e; e = fila.shift()) {
      const destino = path.join(PASTA, e.arquivo)
      if (fs.existsSync(destino) && fs.statSync(destino).size === e.bytes && antes.get(e.id)) {
        e.obtida_de = antes.get(e.id)
        prontas++
        continue
      }
      try {
        const r = await fetch(e.url_arquivo)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        fs.writeFileSync(destino, Buffer.from(await r.arrayBuffer()))
        e.obtida_de = 'site publicado'
        baixadas++
      } catch (erro) {
        const copia = e.origem_legado && path.join(SITE, 'site_legado', 'public', e.origem_legado)
        if (copia && fs.existsSync(copia)) {
          fs.copyFileSync(copia, destino)
          e.obtida_de = 'site legado'
          legado++
        } else {
          e.obtida_de = `[FALTA: arquivo não obtido (${erro.message})]`
          falhas++
        }
      }
    }
  }
  await Promise.all([1, 2, 3, 4].map(trabalhador))

  const hoje = new Date().toISOString().slice(0, 10)
  fs.writeFileSync(CONTEXTO, lista.map((e) => JSON.stringify({ ...e, exportado_em: hoje })).join('\n') + '\n', 'utf8')
  const tipos = {}
  for (const e of lista) for (const u of e.usos) tipos[u.fonte] = (tipos[u.fonte] || 0) + 1
  console.log(`${lista.length} imagens (${usos.length} usos: ${JSON.stringify(tipos)})`)
  console.log(`baixadas ${baixadas}, do legado ${legado}, já prontas ${prontas}, falhas ${falhas}`)
})()
