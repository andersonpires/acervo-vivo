/**
 * Exporta os convênios da página de transparência do site para
 * acervo/transparencia, e mostra o que mudou desde a última exportação.
 *
 * Uso:
 *   node scripts/exportar_transparencia.cjs
 *
 * A contabilidade do Iteva lança os convênios no painel do site; esta é a
 * fonte. Rodar sempre que houver lançamento novo: o script regrava os
 * arquivos, guarda uma cópia datada em historico/ e escreve mudancas.md
 * comparando com a cópia anterior.
 *
 * Só leitura no banco. Depende do projeto do site ao lado deste
 * (SITE_ITEVA, padrão ../site_iteva), de onde vêm o driver pg e a
 * DATABASE_URI.
 *
 * Os valores "com data até a consulta" e "com data futura" são
 * CALCULADOS aqui, pela data de cada parcela. Não provam que a parcela
 * foi liberada: a página pública avisa que as datas são previstas e
 * sujeitas a alteração, e só a contabilidade confirma o recebimento.
 */
const fs = require('fs')
const path = require('path')

const RAIZ = path.resolve(__dirname, '..')
const SITE = path.resolve(process.env.SITE_ITEVA || path.join(RAIZ, '..', 'site_iteva'))
const SAIDA = path.join(RAIZ, 'acervo', 'transparencia')
const HOJE = new Date().toISOString().slice(0, 10)

process.loadEnvFile(path.join(SITE, '.env'))
const { Client } = require(path.join(SITE, 'site_novo', 'node_modules', 'pg'))

// Nome do convênio para projeto do cadastro (projetos/cadastro.csv).
const PROJETOS = [
  [/CONECTIVIDADE/i, 'Conectividade +60'],
  [/MIDIACOM/i, 'Midiacom'],
  [/NOCORRE/i, 'NoCorre'],
  [/BEM.ESTAR/i, 'Bem-estar +60'],
  [/CDF|CIDAD[ÃA]O DO FUTURO/i, 'CDF'],
  [/CONSTRUCOM/i, 'Construcom'],
]

const texto = (n) => (!n ? '' : (n.text || '') + (n.children || []).map(texto).join('') + (n.type === 'paragraph' ? '\n' : ''))
const reais = (v) => {
  const s = String(v || '').replace(/[^\d,.-]/g, '')
  if (!/\d/.test(s)) return null
  return Number(s.replace(/\./g, '').replace(',', '.'))
}
const dataBr = (v) => {
  const m = String(v || '').match(/(\d{2})\/(\d{2})\/(\d{4})/)
  return m ? `${m[3]}-${m[2]}-${m[1]}` : null
}
const brl = (n) => (n == null ? '' : n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))
const slug = (s) =>
  s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

async function ler() {
  const c = new Client({ connectionString: process.env.DATABASE_URI })
  await c.connect()
  const q = async (s, p) => (await c.query(s, p)).rows
  const convenios = await q(`select * from transparencia where situacao = 'publicado' order by data_referencia desc, id`)
  for (const v of convenios) {
    v.tabelas = []
    for (const t of await q('select * from transparencia_tabelas where _parent_id = $1 order by _order', [v.id])) {
      const colunas = (await q('select rotulo from transparencia_tabelas_colunas where _parent_id = $1 order by _order', [t.id])).map((x) => x.rotulo)
      const linhas = []
      for (const l of await q('select id from transparencia_tabelas_linhas where _parent_id = $1 order by _order', [t.id])) {
        linhas.push((await q('select valor from transparencia_tabelas_linhas_celulas where _parent_id = $1 order by _order', [l.id])).map((x) => x.valor ?? ''))
      }
      v.tabelas.push({ titulo: t.titulo, previsao: t.mostrar_previsao, soma: t.somar_valores, colunas, linhas })
    }
  }
  await c.end()
  return convenios
}

function resumir(v) {
  const nome = v.nome
  const projeto = (PROJETOS.find(([r]) => r.test(nome)) || [null, '[FALTA: projeto não reconhecido no nome]'])[1]
  const idt = texto(v.identificacao?.root)
  const municipio =
    (nome.match(/,\s*([^,]+?)\/CE/i) || [])[1] ||
    ((idt.match(/MUNIC[ÍI]PIO DE ([A-ZÁÉÍÓÚÂÊÔÃÕÇ ]+?)(?: E | E\b|,)/) || [])[1] || '').trim() ||
    '[FALTA: município]'
  const parc = v.tabelas.find((t) => /LIBERA/i.test(t.titulo))
  const prest = v.tabelas.find((t) => /PRESTA/i.test(t.titulo))
  let liberado = 0, previsto = 0, n = 0, primeira = null, ultima = null, semData = 0
  for (const l of parc?.linhas || []) {
    const valor = reais(l[1])
    const data = dataBr(l[2])
    if (valor == null) continue
    n++
    if (!data) { semData++; previsto += valor; continue }
    if (data <= HOJE) liberado += valor
    else previsto += valor
    if (!primeira || data < primeira) primeira = data
    if (!ultima || data > ultima) ultima = data
  }
  const resultados = {}
  for (const l of prest?.linhas || []) {
    const r = (l[l.length - 1] || '').trim() || '-'
    const chave = /^aprovad/i.test(r) ? 'aprovada' : r === '-' ? 'sem resultado' : r.toLowerCase()
    resultados[chave] = (resultados[chave] || 0) + 1
  }
  const pendentes = Object.entries(resultados).filter(([k]) => k !== 'aprovada').reduce((s, [, x]) => s + x, 0)
  let situacao
  if (!parc) situacao = 'sem tabela de parcelas'
  else if (previsto > 0) situacao = 'em execução (há parcelas com data futura)'
  else if (prest && pendentes === 0 && (prest.linhas || []).length > 0) situacao = 'concluído (todas as prestações aprovadas)'
  else situacao = 'datas das parcelas vencidas, prestação de contas pendente'
  const aditivo = /aditiv/i.test(idt + texto(v.objeto?.root))
  return {
    id: v.id, nome, projeto, municipio, orgao: v.orgao || '', termo: v.titulo_identificacao || '',
    data_referencia: v.data_referencia ? new Date(v.data_referencia).toISOString().slice(0, 10) : '',
    valor_total: v.valor_total != null ? Number(v.valor_total) : null,
    parcelas: n, soma_parcelas: liberado + previsto, valor_data_ate_consulta: liberado, valor_data_futura: previsto,
    parcelas_sem_data: semData, primeira_parcela: primeira || '', ultima_parcela: ultima || '',
    prestacoes: resultados, situacao_calculada: situacao, cita_aditivo: aditivo,
  }
}

function markdown(v, r) {
  const L = [
    '---',
    `nome: ${JSON.stringify(v.nome)}`,
    `projeto: ${r.projeto}`,
    `municipio: ${r.municipio}`,
    `orgao: ${JSON.stringify(r.orgao)}`,
    `termo: ${JSON.stringify(r.termo)}`,
    `data_referencia: ${r.data_referencia}`,
    `valor_total: ${r.valor_total ?? ''}`,
    `fonte: https://www.iteva.org.br/transparencia (banco do site, id ${v.id})`,
    `consultado_em: ${HOJE}`,
    '---',
    '',
    `# ${v.nome}`,
    '',
    '## Resumo calculado',
    '',
    `Calculado por \`scripts/exportar_transparencia.cjs\` em ${HOJE}, a partir das tabelas abaixo. As datas da página pública são "previstas, sujeitas a alteração".`,
    '',
    `- Valor total do convênio: R$ ${brl(r.valor_total)}`,
    `- Parcelas: ${r.parcelas}, somando R$ ${brl(r.soma_parcelas)}`,
    `- Parcelas com data até ${HOJE}: R$ ${brl(r.valor_data_ate_consulta)} (a data não prova a liberação)`,
    `- Parcelas com data depois de ${HOJE}: R$ ${brl(r.valor_data_futura)}`,
    `- Primeira e última parcela: ${r.primeira_parcela || '-'} e ${r.ultima_parcela || '-'}`,
    `- Prestação de contas: ${Object.entries(r.prestacoes).map(([k, x]) => `${x} ${k}`).join(', ') || 'sem tabela'}`,
    `- Situação calculada: ${r.situacao_calculada}`,
  ]
  if (r.cita_aditivo) L.push('- O texto do convênio cita termo aditivo (ver Identificação).')
  if (r.valor_total != null && Math.abs(r.valor_total - r.soma_parcelas) > 0.01 && r.parcelas)
    L.push(`- A soma das parcelas difere do valor total em R$ ${brl(r.valor_total - r.soma_parcelas)}.`)
  L.push('', `## Identificação: ${r.termo}`, '', texto(v.identificacao?.root).trim() || '(vazio)', '', '## Objeto', '', texto(v.objeto?.root).trim() || '(vazio)', '')
  for (const t of v.tabelas) {
    L.push(`## ${t.titulo}`, '')
    if (t.previsao) L.push('*Datas previstas, sujeitas a alteração (aviso da página pública).*', '')
    L.push('| ' + t.colunas.join(' | ') + ' |', '|' + t.colunas.map(() => '---').join('|') + '|')
    for (const l of t.linhas) L.push('| ' + l.map((x) => String(x).replace(/\|/g, '/')).join(' | ') + ' |')
    L.push('')
  }
  return L.join('\n')
}

function csv(linhas) {
  const cols = ['id', 'nome', 'projeto', 'municipio', 'orgao', 'termo', 'data_referencia', 'valor_total', 'parcelas', 'soma_parcelas',
    'valor_data_ate_consulta', 'valor_data_futura', 'primeira_parcela', 'ultima_parcela', 'prestacoes', 'situacao_calculada', 'cita_aditivo']
  const fmt = (k, v) => (typeof v === 'number' && k !== 'id' && k !== 'parcelas' ? brl(v) : k === 'prestacoes' ? Object.entries(v).map(([a, b]) => `${b} ${a}`).join(', ') : v === true ? 'sim' : v === false ? '' : String(v ?? ''))
  const esc = (s) => (/[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s)
  return '﻿' + [cols.join(';'), ...linhas.map((r) => cols.map((k) => esc(fmt(k, r[k]))).join(';'))].join('\r\n') + '\r\n'
}

function mudancas(antes, agora) {
  if (!antes) return ['Primeira exportação: não há cópia anterior para comparar.']
  const A = new Map(antes.map((r) => [r.id, r]))
  const B = new Map(agora.map((r) => [r.id, r]))
  const out = []
  for (const [id, r] of B) if (!A.has(id)) out.push(`- **Novo convênio:** ${r.nome} (R$ ${brl(r.valor_total)})`)
  for (const [id, r] of A) if (!B.has(id)) out.push(`- **Saiu da página:** ${r.nome}`)
  const campos = ['valor_total', 'parcelas', 'soma_parcelas', 'valor_data_ate_consulta', 'situacao_calculada', 'termo', 'cita_aditivo']
  for (const [id, r] of B) {
    const a = A.get(id)
    if (!a) continue
    for (const k of campos) {
      const x = JSON.stringify(a[k]), y = JSON.stringify(r[k])
      if (x !== y) out.push(`- ${r.nome}: **${k}** de ${x} para ${y}`)
    }
    if (JSON.stringify(a.prestacoes) !== JSON.stringify(r.prestacoes))
      out.push(`- ${r.nome}: **prestação de contas** de ${JSON.stringify(a.prestacoes)} para ${JSON.stringify(r.prestacoes)}`)
  }
  return out.length ? out : ['Nenhuma mudança desde a exportação anterior.']
}

;(async () => {
  const convenios = await ler()
  const dirConv = path.join(SAIDA, 'convenios')
  const dirHist = path.join(SAIDA, 'historico')
  fs.mkdirSync(dirHist, { recursive: true })
  if (fs.existsSync(dirConv)) for (const f of fs.readdirSync(dirConv)) fs.unlinkSync(path.join(dirConv, f))
  fs.mkdirSync(dirConv, { recursive: true })

  const resumos = []
  for (const v of convenios) {
    const r = resumir(v)
    resumos.push(r)
    const nomeArq = `${(r.data_referencia || '0000').slice(0, 4)}-${slug(v.nome)}.md`
    fs.writeFileSync(path.join(dirConv, nomeArq), markdown(v, r), 'utf8')
  }
  fs.writeFileSync(path.join(SAIDA, 'resumo.csv'), csv(resumos), 'utf8')

  const anteriores = fs.readdirSync(dirHist).filter((f) => f.endsWith('.json') && f !== `${HOJE}.json`).sort()
  const antes = anteriores.length ? JSON.parse(fs.readFileSync(path.join(dirHist, anteriores.at(-1)), 'utf8')) : null
  fs.writeFileSync(path.join(dirHist, `${HOJE}.json`), JSON.stringify(resumos, null, 1), 'utf8')
  const linhas = [
    '# Mudanças na transparência',
    '',
    `Exportação de ${HOJE}, comparada com ${anteriores.length ? anteriores.at(-1).replace('.json', '') : '(nenhuma)'}.`,
    '',
    ...mudancas(antes, resumos),
    '',
  ]
  fs.writeFileSync(path.join(SAIDA, 'mudancas.md'), linhas.join('\n'), 'utf8')

  // O que a contabilidade precisa conferir: falta de tabela ou números que não fecham.
  const conf = ['# A conferir na transparência', '',
    `Gerado em ${HOJE} por \`scripts/exportar_transparencia.cjs\`. Não é erro confirmado: são pontos em que a página pública não fecha sozinha e só a contabilidade sabe a resposta (aditivo, devolução, lançamento pendente).`, '']
  for (const r of resumos) {
    const itens = []
    if (!r.parcelas) itens.push('sem tabela de parcelas liberadas')
    if (!Object.keys(r.prestacoes).length) itens.push('sem tabela de situação da prestação de contas')
    if (r.parcelas && r.valor_total != null && Math.abs(r.valor_total - r.soma_parcelas) > 0.01)
      itens.push(`soma das parcelas (R$ ${brl(r.soma_parcelas)}) ${r.soma_parcelas > r.valor_total ? 'maior' : 'menor'} que o valor total (R$ ${brl(r.valor_total)}): aditivo, devolução ou parcela não lançada?`)
    for (const [k, x] of Object.entries(r.prestacoes)) if (/atraso|aguard/i.test(k)) itens.push(`prestação "${k}" (${x})`)
    if (r.cita_aditivo) itens.push('o texto cita termo aditivo; o valor total já o inclui?')
    if (itens.length) conf.push(`## ${r.nome}`, '', ...itens.map((i) => `- ${i}`), '')
  }
  fs.writeFileSync(path.join(SAIDA, 'conferir.md'), conf.join('\n'), 'utf8')

  // Linhas do índice do acervo (scripts/montar_indice.py lê esta pasta).
  const idx = resumos.map((r) => JSON.stringify({
    fonte: 'transparencia', arquivo: `transparencia/convenios/${(r.data_referencia || '0000').slice(0, 4)}-${slug(r.nome)}.md`,
    ano: Number((r.data_referencia || '').slice(0, 4)) || null, titulo: r.nome,
    projetos: r.projeto.startsWith('[FALTA') ? ['Institucional'] : [r.projeto],
    paginas_ou_url: 'https://www.iteva.org.br/transparencia', tipo: 'convênio',
    obs: `${r.termo}; R$ ${brl(r.valor_total)}; ${r.situacao_calculada}; consultado em ${HOJE}`,
  }))
  fs.writeFileSync(path.join(RAIZ, 'scripts', 'indexacao', 'transparencia.jsonl'), idx.join('\n') + '\n', 'utf8')

  const tot = resumos.reduce((s, r) => s + (r.valor_total || 0), 0)
  console.log(`${resumos.length} convênios, R$ ${brl(tot)} no total; mudanças em acervo/transparencia/mudancas.md`)
})()
