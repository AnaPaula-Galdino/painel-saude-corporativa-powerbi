# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,"src")
from relatorio_exec import construir

cfg = {
 "fonte":"Ana Paula Galdino · Painel Executivo de Saúde Corporativa (dados fictícios)",
 "eyebrow":"PAINEL EXECUTIVO · SAÚDE CORPORATIVA",
 "titulo":"Sinistralidade e Custos Assistenciais",
 "subtitulo":"Gestão de carteira de saúde corporativa — Power BI + Python",
 "meta":"Período: jan/2024 a dez/2025 · 6 carteiras · 24 meses · dados fictícios para demonstração",
 "sumario":[
   "Este relatório consolida a performance de uma carteira de saúde corporativa, com foco em <b>sinistralidade</b>, "
   "<b>custo per capita (PMPM)</b> e <b>utilização assistencial</b>. O modelo foi construído em esquema estrela "
   "(duas fatos e cinco dimensões), com medidas DAX e visualização em Power BI.",
   "No acumulado, a sinistralidade global ficou em <b>74,0%</b>, ligeiramente abaixo da meta de 75%, mas com "
   "<b>três das seis carteiras acima do teto</b> — metade da base concentra o risco e exige ação prioritária."
 ],
 "kpis":[("74,0%","Sinistralidade"),("R$ 428","PMPM"),("R$ 93,6M","Receita (24m)"),
         ("R$ 69,3M","Custo assistencial"),("R$ 24,3M","Resultado"),("6.743","Vidas/mês")],
 "secoes":[
   {"titulo":"1. Visão executiva",
    "texto":[
      "A carteira manteve resultado positivo no período (margem de 26%), com receita de mensalidades crescendo de "
      "forma consistente acompanhada de perto pelo custo assistencial. A sinistralidade mensal oscilou em torno da "
      "meta, com picos no inverno (junho a agosto), padrão típico do aumento de doenças respiratórias.",
      "As <b>Internações</b> são o principal vetor de custo, seguidas de <b>Exames</b> — juntas respondem pela maior "
      "parte do gasto, ainda que representem a minoria dos atendimentos."],
    "imagens":[("imagens/painel_1_visao_executiva.png","Página 1 — Visão executiva consolidada")]},
   {"titulo":"2. Sinistralidade e decomposição de custos",
    "texto":[
      "A análise por carteira revela forte dispersão: enquanto empresas como a TechNova e a AgroFértil operam "
      "saudáveis (~68%), <b>Saúde&amp;Vida Clínicas (86,9%)</b>, <b>LogPlus Transportes (80,9%)</b> e "
      "<b>Construtora Horizonte (76,6%)</b> superam a meta e puxam o indicador global. O custo cresce de forma "
      "acentuada nas faixas etárias mais altas (46-59 e 60+), refletindo o maior fator de risco desse público.",
      "O PMPM por plano evidencia o esperado: o plano Apartamento tem o maior custo por vida, o que deve ser "
      "considerado na precificação e na estratégia de migração de planos."],
    "imagens":[("imagens/painel_2_sinistralidade_custos.png","Página 2 — Sinistralidade e custos")]},
   {"titulo":"3. Utilização e tendências",
    "texto":[
      "O volume de atendimentos é dominado por consultas e exames, mas o <b>Pronto-Socorro</b> merece atenção: parte "
      "relevante dessas idas é evitável e poderia ser redirecionada à atenção primária, reduzindo custo e "
      "internações subsequentes. A variação mês a mês permite antecipar sazonalidades e planejar campanhas de "
      "prevenção nos períodos críticos."],
    "imagens":[("imagens/painel_3_utilizacao_tendencias.png","Página 3 — Utilização e tendências")]},
 ],
 "conclusao_titulo":"Recomendações",
 "conclusoes":[
   "<b>Atacar as três carteiras acima da meta</b> (Saúde&amp;Vida, LogPlus e Construtora) com gestão de casos crônicos e auditoria de internações.",
   "<b>Reduzir idas evitáveis ao Pronto-Socorro</b> via atenção primária e telemedicina, mirando as faixas de maior utilização.",
   "<b>Programas de prevenção sazonais</b> (vacinação e campanhas no inverno) para suavizar os picos de sinistralidade.",
   "<b>Revisar precificação e mix de planos</b> nas carteiras de maior PMPM, alinhando preço ao risco real.",
   "<b>Monitorar PMPM e sinistralidade YoY mensalmente</b> no painel, com alertas automáticos ao ultrapassar a meta."
 ],
}
construir(cfg, "relatorio/Relatorio_Executivo_Saude_Corporativa.pdf")
