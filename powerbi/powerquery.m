// ============================================================
//  Power Query (M) - Ingestão e transformação
//  Painel Executivo de Saúde Corporativa
//  Autora: Ana Paula Galdino
//  Observação: ajuste "PastaDados" para o caminho da pasta /dados.
// ============================================================

// ---------- Parâmetro de caminho ----------
// PastaDados = "C:\...\projeto-powerbi-saude\dados\"

// ---------- fato_sinistros ----------
let
    Origem = Csv.Document(
        File.Contents(PastaDados & "fato_sinistros.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Promovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Promovido, {
        {"mes_id", Int64.Type}, {"empresa_id", type text}, {"plano_id", type text},
        {"categoria_id", type text}, {"faixa_id", type text},
        {"custo", type number}, {"qtd", Int64.Type}
    }),
    SemNulos = Table.SelectRows(Tipos, each [custo] <> null and [custo] >= 0)
in
    SemNulos

// ---------- fato_carteira ----------
let
    Origem = Csv.Document(
        File.Contents(PastaDados & "fato_carteira.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Promovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Promovido, {
        {"mes_id", Int64.Type}, {"empresa_id", type text}, {"plano_id", type text},
        {"vidas", Int64.Type}, {"receita", type number}
    })
in
    Tipos

// ---------- dim_tempo ----------
let
    Origem = Csv.Document(
        File.Contents(PastaDados & "dim_tempo.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Promovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Promovido, {
        {"data", type date}, {"mes_id", Int64.Type}, {"ano", Int64.Type},
        {"mes", Int64.Type}, {"mes_nome", type text}, {"trimestre", type text}
    }),
    MarcaCalendario = Table.AddColumn(Tipos, "AnoMes", each Text.From([ano]) & "-" & Text.PadStart(Text.From([mes]),2,"0"), type text)
in
    MarcaCalendario

// ---------- dim_empresa / dim_plano / dim_categoria / dim_faixa ----------
// (mesmo padrão: Csv.Document -> PromoteHeaders -> TransformColumnTypes)
let
    Carregar = (arquivo as text) as table =>
        let
            o = Csv.Document(File.Contents(PastaDados & arquivo),
                    [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            h = Table.PromoteHeaders(o, [PromoteAllScalars=true])
        in
            h
in
    Carregar  // uso: Carregar("dim_empresa.csv"), Carregar("dim_plano.csv"), ...
