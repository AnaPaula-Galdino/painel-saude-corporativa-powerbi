# -*- coding: utf-8 -*-
"""
Gera o dataset FICTÍCIO da carteira de saúde corporativa em esquema estrela.
Saída: /dados (dimensões + duas tabelas-fato). Sinistralidade global calibrada ~74%.
Autora: Ana Paula Galdino
"""
import numpy as np, pandas as pd, os
np.random.seed(42)
OUT = "dados"; os.makedirs(OUT, exist_ok=True)

# ---------------- Dimensões ----------------
dim_empresa = pd.DataFrame([
 ("E01","TechNova Indústria","Indústria",1),("E02","Construtora Horizonte","Construção",2),
 ("E03","Varejo BomPreço","Varejo",3),("E04","LogPlus Transportes","Logística",4),
 ("E05","Saúde&Vida Clínicas","Serviços",5),("E06","AgroFértil","Agronegócio",6),
], columns=["empresa_id","empresa","setor","porte_rank"])

dim_plano = pd.DataFrame([("P1","Ambulatorial"),("P2","Enfermaria"),("P3","Apartamento")],
                         columns=["plano_id","plano"])

dim_categoria = pd.DataFrame([
 ("C1","Consultas",0.18,0.10),("C2","Exames",0.27,0.16),("C3","Terapias",0.12,0.10),
 ("C4","Internações",0.28,0.45),("C5","Pronto-Socorro",0.10,0.12),("C6","Odontológico",0.05,0.07),
], columns=["categoria_id","categoria","peso_freq","peso_custo"])

dim_faixa = pd.DataFrame([("F1","0-18",0.7),("F2","19-30",0.8),("F3","31-45",1.0),
                          ("F4","46-59",1.6),("F5","60+",2.8)],
                         columns=["faixa_id","faixa_etaria","fator_risco"])

meses = pd.date_range("2024-01-01","2025-12-01",freq="MS")
dim_tempo = pd.DataFrame({"data":meses})
dim_tempo["mes_id"]=dim_tempo["data"].dt.strftime("%Y%m").astype(int)
dim_tempo["ano"]=dim_tempo["data"].dt.year
dim_tempo["mes"]=dim_tempo["data"].dt.month
dim_tempo["mes_nome"]=dim_tempo["data"].dt.strftime("%b/%y")
dim_tempo["trimestre"]="T"+dim_tempo["data"].dt.quarter.astype(str)+"/"+dim_tempo["ano"].astype(str)

# ---------------- Carteira (vidas + receita) ----------------
base_vidas={"E01":1400,"E02":620,"E03":2100,"E04":880,"E05":540,"E06":760}
plano_mix={"P1":0.55,"P2":0.30,"P3":0.15}
preco_base={"P1":410,"P2":640,"P3":1080}
rows=[]
for _,e in dim_empresa.iterrows():
    for i,(_,t) in enumerate(dim_tempo.iterrows()):
        total=int(base_vidas[e.empresa_id]*(1+0.006*i+np.random.normal(0,0.01)))
        for _,p in dim_plano.iterrows():
            vidas=max(int(total*plano_mix[p.plano_id]*(1+np.random.normal(0,0.03))),0)
            receita=round(vidas*preco_base[p.plano_id]*(1+np.random.normal(0,0.02)),2)
            rows.append((t.mes_id,e.empresa_id,p.plano_id,vidas,receita))
fato_carteira=pd.DataFrame(rows,columns=["mes_id","empresa_id","plano_id","vidas","receita"])

# ---------------- Sinistros (custo + qtd) ----------------
rng=np.random.default_rng(7)
emp_factor={"E01":0.92,"E02":1.02,"E03":0.97,"E04":1.08,"E05":1.15,"E06":0.90}
faixa_mix=dict(zip(dim_faixa.faixa_id,[0.18,0.24,0.26,0.20,0.12]))
rows=[]
for _,c in fato_carteira.iterrows():
    m=dim_tempo[dim_tempo.mes_id==c.mes_id].iloc[0]
    season=1.0+0.10*np.exp(-((m.mes-7)**2)/8.0)
    target=np.clip(0.66*emp_factor[c.empresa_id]*season+rng.normal(0,0.03),0.45,1.05)
    custo_total=c.receita*target
    for _,f in dim_faixa.iterrows():
        for _,cat in dim_categoria.iterrows():
            share=faixa_mix[f.faixa_id]*f.fator_risco*cat.peso_custo
            rows.append((c.mes_id,c.empresa_id,c.plano_id,cat.categoria_id,f.faixa_id,custo_total*share))
fato=pd.DataFrame(rows,columns=["mes_id","empresa_id","plano_id","categoria_id","faixa_id","custo"])

# calibra sinistralidade global para ~74% preservando a estrutura relativa
scale=0.74*fato_carteira.receita.sum()/fato.custo.sum()
fato["custo"]=(fato["custo"]*scale).round(2)
ticket={"C1":190,"C2":160,"C3":140,"C4":7200,"C5":520,"C6":210}
fato["qtd"]=fato.apply(lambda r:max(int(r.custo/ticket[r.categoria_id]*(1+rng.normal(0,0.05))),0),axis=1)

# ---------------- Exporta ----------------
dim_empresa.to_csv(f"{OUT}/dim_empresa.csv",index=False)
dim_plano.to_csv(f"{OUT}/dim_plano.csv",index=False)
dim_categoria.to_csv(f"{OUT}/dim_categoria.csv",index=False)
dim_faixa.to_csv(f"{OUT}/dim_faixa.csv",index=False)
dim_tempo.to_csv(f"{OUT}/dim_tempo.csv",index=False)
fato_carteira.to_csv(f"{OUT}/fato_carteira.csv",index=False)
fato.to_csv(f"{OUT}/fato_sinistros.csv",index=False)
print("OK · sinistralidade global: %.1f%%"%(100*fato.custo.sum()/fato_carteira.receita.sum()))
