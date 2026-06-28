# -*- coding: utf-8 -*-
"""
Renderiza as telas do Painel Executivo de Saude Corporativa no estilo Power BI.
Gera 3 imagens em alta fidelidade (1600x900) a partir do modelo estrela em /dados.
Autora: Ana Paula Galdino
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Wedge, Circle
from matplotlib import font_manager

D = "dados"; IMG = "imagens"
emp = pd.read_csv(f"{D}/dim_empresa.csv")
plano = pd.read_csv(f"{D}/dim_plano.csv")
cat = pd.read_csv(f"{D}/dim_categoria.csv")
faixa = pd.read_csv(f"{D}/dim_faixa.csv")
tempo = pd.read_csv(f"{D}/dim_tempo.csv")
cart = pd.read_csv(f"{D}/fato_carteira.csv")
fato = pd.read_csv(f"{D}/fato_sinistros.csv")

# paleta estilo Power BI (tema "Executivo Azul")
NAVY="#1f3a5f"; BLUE="#2e6da4"; TEAL="#2a9d9d"; LBLUE="#5b9bd5"
GREY="#6b7280"; LGREY="#aeb6c2"; BG="#f3f4f7"; CARD="#ffffff"
GREEN="#2e9e6b"; RED="#d2553f"; AMBER="#e0a93b"
PAL=[NAVY,TEAL,BLUE,LBLUE,"#7fb0d8","#9bd1c9"]
plt.rcParams["font.family"]="DejaVu Sans"
plt.rcParams["axes.edgecolor"]=LGREY

def brl(v, mi=False):
    if mi: return f"R$ {v/1e6:.1f}M".replace(".",",")
    return ("R$ "+f"{v:,.0f}").replace(",",".")
def pct(v): return f"{v*100:.1f}%".replace(".",",")
def num(v): return f"{v:,.0f}".replace(",",".")

# ---- agregacoes base ----
fc = fato.merge(tempo[["mes_id","mes_nome","mes","ano","data"]],on="mes_id")
cc = cart.merge(tempo[["mes_id","mes_nome","mes","ano","data"]],on="mes_id")
rec_tot=cart.receita.sum(); cus_tot=fato.custo.sum()
sin_glob=cus_tot/rec_tot
vidas_med=cart.groupby("mes_id").vidas.sum().mean()
pmpm=cus_tot/cart.vidas.sum()
resultado=rec_tot-cus_tot
atend_tot=fato.qtd.sum()

mes_ord=tempo.sort_values("mes_id")
serie=pd.DataFrame({"mes_id":mes_ord.mes_id,"mes_nome":mes_ord.mes_nome})
serie=serie.merge(cart.groupby("mes_id").receita.sum().rename("receita"),on="mes_id")
serie=serie.merge(fato.groupby("mes_id").custo.sum().rename("custo"),on="mes_id")
serie=serie.merge(cart.groupby("mes_id").vidas.sum().rename("vidas"),on="mes_id")
serie["sin"]=serie.custo/serie.receita
serie["pmpm"]=serie.custo/serie.vidas

por_cat=fato.merge(cat,on="categoria_id").groupby("categoria").custo.sum().sort_values(ascending=False)
por_emp=(fato.groupby("empresa_id").custo.sum()/cart.groupby("empresa_id").receita.sum())
por_emp=por_emp.reset_index(name="sin").merge(emp,on="empresa_id").sort_values("sin")
por_faixa=fato.merge(faixa,on="faixa_id").groupby("faixa_etaria").custo.sum()
por_faixa=por_faixa.reindex(["0-18","19-30","31-45","46-59","60+"])
pmpm_plano=(fato.groupby("plano_id").custo.sum()/cart.groupby("plano_id").vidas.sum())
pmpm_plano=pmpm_plano.reset_index(name="pmpm").merge(plano,on="plano_id").sort_values("pmpm")

# ---------- helpers de layout ----------
def base_canvas(title, subtitle, page):
    fig=plt.figure(figsize=(16,9),dpi=100); fig.patch.set_facecolor(BG)
    bg=fig.add_axes([0,0,1,1]); bg.set_xlim(0,1); bg.set_ylim(0,1); bg.axis("off")
    # header
    bg.add_patch(FancyBboxPatch((0,0.915),1,0.09,boxstyle="square,pad=0",fc=NAVY,ec="none"))
    bg.add_patch(plt.Rectangle((0.018,0.95),0.006,0.028,fc=TEAL,ec="none"))
    bg.text(0.032,0.963,title,color="white",fontsize=20,fontweight="bold",va="center")
    bg.text(0.032,0.935,subtitle,color="#c7d3e6",fontsize=11,va="center")
    bg.text(0.985,0.963,"Saúde Corporativa",color="#9fb4d6",fontsize=12,ha="right",va="center",fontweight="bold")
    bg.text(0.985,0.935,page,color="#7e93b8",fontsize=9.5,ha="right",va="center")
    return fig,bg

def card(bg,x,y,w,h,label,value,delta=None,dcolor=GREY,vcolor=NAVY,vsize=23):
    bg.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.004,rounding_size=0.012",
                 fc=CARD,ec="#e3e7ee",lw=1))
    bg.text(x+0.014,y+h-0.022,label,color=GREY,fontsize=10.5,va="center")
    bg.text(x+0.014,y+h*0.40,value,color=vcolor,fontsize=vsize,fontweight="bold",va="center")
    if delta:
        bg.text(x+0.014,y+0.020,delta,color=dcolor,fontsize=10,va="center",fontweight="bold")

def panel(fig,x,y,w,h,title):
    bg=fig.axes[0]
    bg.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.004,rounding_size=0.012",
                 fc=CARD,ec="#e3e7ee",lw=1))
    bg.text(x+0.013,y+h-0.028,title,color=NAVY,fontsize=12.5,fontweight="bold",va="center")
    ax=fig.add_axes([x+0.016,y+0.022,w-0.032,h-0.085]); ax.set_facecolor(CARD)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color(LGREY)
    ax.tick_params(colors=GREY,labelsize=9)
    return ax

# ===================== PÁGINA 1 — VISÃO EXECUTIVA =====================
fig,bg=base_canvas("Painel Executivo — Saúde Corporativa",
                   "Visão consolidada da carteira  ·  jan/2024 a dez/2025  ·  dados fictícios",
                   "Página 1 de 3  ·  Visão Executiva")
cy=0.775; ch=0.115; cw=0.150; gap=0.0095; x0=0.018
kpis=[("Sinistralidade",pct(sin_glob),"Meta 75,0%  ·  -1,0 p.p.",GREEN,NAVY),
      ("Receita (24m)",brl(rec_tot,True),"Mensalidades",GREY,NAVY),
      ("Custo assistencial",brl(cus_tot,True),"Sinistros",GREY,NAVY),
      ("Resultado",brl(resultado,True),"Margem 26,0%",GREEN,GREEN),
      ("PMPM",brl(pmpm),"Custo médio/vida·mês",GREY,NAVY),
      ("Vidas (média/mês)",num(vidas_med),"6 carteiras",GREY,NAVY)]
for i,(l,v,d,dc,vc) in enumerate(kpis):
    card(bg,x0+i*(cw+gap),cy,cw,ch,l,v,d,dc,vc,vsize=20)

# Receita vs Custo
ax=panel(fig,0.018,0.40,0.46,0.345,"Receita vs. Custo assistencial (R$ mi)")
xs=range(len(serie))
ax.plot(xs,serie.receita/1e6,color=BLUE,lw=2.4,marker="o",ms=3,label="Receita")
ax.fill_between(xs,serie.custo/1e6,color=TEAL,alpha=0.18)
ax.plot(xs,serie.custo/1e6,color=TEAL,lw=2.4,marker="o",ms=3,label="Custo")
ax.set_xticks(list(xs)[::3]); ax.set_xticklabels(serie.mes_nome[::3],rotation=0)
ax.legend(loc="upper left",frameon=False,fontsize=9,ncol=2)
ax.grid(axis="y",color="#eef1f6")

# Sinistralidade mensal com meta
ax=panel(fig,0.49,0.40,0.49,0.345,"Sinistralidade mensal vs. meta")
ax.plot(xs,serie.sin*100,color=NAVY,lw=2.6,marker="o",ms=3)
ax.axhline(75,color=RED,ls="--",lw=1.6)
ax.text(len(xs)-1,75.4,"meta 75%",color=RED,fontsize=9,ha="right")
ax.fill_between(xs,serie.sin*100,75,where=(serie.sin*100>=75),color=RED,alpha=0.10)
ax.set_xticks(list(xs)[::3]); ax.set_xticklabels(serie.mes_nome[::3])
ax.set_ylim(55,95); ax.grid(axis="y",color="#eef1f6")

# Custo por categoria (donut)
ax=panel(fig,0.018,0.022,0.30,0.36,"Custo por categoria")
w,_=ax.pie(por_cat.values,colors=PAL,startangle=90,counterclock=False,
           wedgeprops=dict(width=0.42,edgecolor="white",lw=1.5))
ax.add_artist(Circle((0,0),0.30,fc=CARD,ec="none"))
ax.text(0,0.08,pct(sin_glob),ha="center",fontsize=15,fontweight="bold",color=NAVY)
ax.text(0,-0.16,"sinistr.",ha="center",fontsize=9,color=GREY)
ax.legend(por_cat.index,loc="center left",bbox_to_anchor=(0.95,0.5),frameon=False,fontsize=8.5)
ax.set_aspect("equal")

# Sinistralidade por empresa
ax=panel(fig,0.33,0.022,0.65,0.36,"Sinistralidade por empresa (carteira)")
cores=[RED if s>=0.75 else (AMBER if s>=0.72 else TEAL) for s in por_emp.sin]
b=ax.barh(por_emp.empresa,por_emp.sin*100,color=cores,height=0.62)
ax.axvline(75,color=RED,ls="--",lw=1.4); ax.text(75.3,5.3,"meta 75%",color=RED,fontsize=8.5)
for r,s in zip(b,por_emp.sin): ax.text(s*100+0.4,r.get_y()+r.get_height()/2,pct(s),va="center",fontsize=9,color=NAVY)
ax.set_xlim(0,95); ax.invert_yaxis(); ax.grid(axis="x",color="#eef1f6")
fig.savefig(f"{IMG}/painel_1_visao_executiva.png",facecolor=BG,bbox_inches="tight")
plt.close(fig)

# ===================== PÁGINA 2 — SINISTRALIDADE & CUSTOS =====================
fig,bg=base_canvas("Painel Executivo — Saúde Corporativa",
                   "Decomposição de custos e risco da carteira  ·  dados fictícios",
                   "Página 2 de 3  ·  Sinistralidade & Custos")
tk_int=fato[fato.categoria_id=="C4"].custo.sum()/max(fato[fato.categoria_id=="C4"].qtd.sum(),1)
n_acima=int((por_emp.sin>0.75).sum()); n_emp=len(por_emp)
kpis2=[("Custo total",brl(cus_tot,True),"24 meses",GREY,NAVY),
       ("Sinistralidade",pct(sin_glob),"meta 75,0%",GREEN,NAVY),
       ("PMPM",brl(pmpm),"por vida/mês",GREY,NAVY),
       ("Ticket internação",brl(tk_int),"custo médio",GREY,NAVY),
       ("% Internações",pct(por_cat["Internações"]/cus_tot),"do custo total",GREY,NAVY),
       ("Carteiras > meta",f"{n_acima} de {n_emp}","ação prioritária",RED,RED)]
for i,(l,v,d,dc,vc) in enumerate(kpis2):
    card(bg,x0+i*(cw+gap),cy,cw,ch,l,v,d,dc,vc,vsize=20)

# Custo por categoria ao longo do tempo (stacked area)
ax=panel(fig,0.018,0.40,0.62,0.345,"Evolução do custo por categoria (R$ mi)")
piv=fc.merge(cat,on="categoria_id").pivot_table(index="mes_id",columns="categoria",values="custo",aggfunc="sum")
piv=piv.reindex(mes_ord.mes_id)
ax.stackplot(range(len(piv)),[piv[c].values/1e6 for c in por_cat.index],labels=list(por_cat.index),colors=PAL,alpha=0.92)
ax.set_xticks(range(0,len(piv),3)); ax.set_xticklabels(serie.mes_nome[::3])
ax.legend(loc="upper left",frameon=False,fontsize=8,ncol=3); ax.grid(axis="y",color="#eef1f6")

# Custo por faixa etaria
ax=panel(fig,0.645,0.40,0.335,0.345,"Custo por faixa etária (R$ mi)")
b=ax.bar(por_faixa.index,por_faixa.values/1e6,color=[LBLUE,BLUE,TEAL,"#1f7a7a",NAVY],width=0.62)
for r,v in zip(b,por_faixa.values): ax.text(r.get_x()+r.get_width()/2,v/1e6+0.3,f"{v/1e6:.1f}".replace('.',','),ha="center",fontsize=9,color=NAVY)
ax.grid(axis="y",color="#eef1f6"); ax.set_ylim(0,por_faixa.max()/1e6*1.18)

# PMPM por plano
ax=panel(fig,0.018,0.022,0.46,0.36,"PMPM por plano (R$/vida·mês)")
b=ax.bar(pmpm_plano.plano,pmpm_plano.pmpm,color=[TEAL,BLUE,NAVY],width=0.55)
for r,v in zip(b,pmpm_plano.pmpm): ax.text(r.get_x()+r.get_width()/2,v+8,brl(v),ha="center",fontsize=9.5,color=NAVY)
ax.grid(axis="y",color="#eef1f6"); ax.set_ylim(0,pmpm_plano.pmpm.max()*1.2)

# Top categorias (ranking horizontal)
ax=panel(fig,0.49,0.022,0.49,0.36,"Ranking de custo por categoria")
pc=por_cat.sort_values()
b=ax.barh(pc.index,pc.values/1e6,color=TEAL,height=0.6)
for r,v in zip(b,pc.values): ax.text(v/1e6+0.2,r.get_y()+r.get_height()/2,f"{v/1e6:.1f} mi".replace('.',','),va="center",fontsize=9,color=NAVY)
ax.set_xlim(0,pc.max()/1e6*1.15); ax.grid(axis="x",color="#eef1f6")
fig.savefig(f"{IMG}/painel_2_sinistralidade_custos.png",facecolor=BG,bbox_inches="tight")
plt.close(fig)

# ===================== PÁGINA 3 — UTILIZAÇÃO & TENDÊNCIAS =====================
fig,bg=base_canvas("Painel Executivo — Saúde Corporativa",
                   "Utilização assistencial e tendências  ·  dados fictícios",
                   "Página 3 de 3  ·  Utilização & Tendências")
qtd_int=fato[fato.categoria_id=="C4"].qtd.sum()
ps_share=fato[fato.categoria_id=="C5"].qtd.sum()/atend_tot
# YoY custo
c2024=fc[fc.ano==2024].custo.sum(); c2025=fc[fc.ano==2025].custo.sum()
yoy=c2025/c2024-1
kpis3=[("Atendimentos (24m)",num(atend_tot),"todas categorias",GREY,NAVY),
       ("Internações",num(qtd_int),"eventos",GREY,NAVY),
       ("% Pronto-Socorro",pct(ps_share),"dos atendimentos",AMBER,NAVY),
       ("Custo 2025 vs 2024",("+" if yoy>=0 else "")+pct(yoy),"variação YoY",RED if yoy>0 else GREEN,RED if yoy>0 else GREEN),
       ("PMPM",brl(pmpm),"por vida/mês",GREY,NAVY),
       ("Sinistralidade",pct(sin_glob),"meta 75,0%",GREEN,NAVY)]
for i,(l,v,d,dc,vc) in enumerate(kpis3):
    card(bg,x0+i*(cw+gap),cy,cw,ch,l,v,d,dc,vc,vsize=19)

# Atendimentos por categoria ao longo do tempo (stacked area)
ax=panel(fig,0.018,0.40,0.62,0.345,"Atendimentos por categoria (mil)")
pivq=fc.merge(cat,on="categoria_id").pivot_table(index="mes_id",columns="categoria",values="qtd",aggfunc="sum").reindex(mes_ord.mes_id)
order_q=fato.merge(cat,on="categoria_id").groupby("categoria").qtd.sum().sort_values(ascending=False).index
ax.stackplot(range(len(pivq)),[pivq[c].values/1e3 for c in order_q],labels=list(order_q),colors=PAL,alpha=0.92)
ax.set_xticks(range(0,len(pivq),3)); ax.set_xticklabels(serie.mes_nome[::3])
ax.legend(loc="upper left",frameon=False,fontsize=8,ncol=3); ax.grid(axis="y",color="#eef1f6")

# Variação MoM do custo
ax=panel(fig,0.645,0.40,0.335,0.345,"Variação mensal do custo (MoM)")
mom=serie.custo.pct_change().fillna(0)*100
cores=[GREEN if v<0 else RED for v in mom]
ax.bar(range(len(mom)),mom,color=cores,width=0.7)
ax.axhline(0,color=GREY,lw=0.8)
ax.set_xticks(range(0,len(mom),3)); ax.set_xticklabels(serie.mes_nome[::3]); ax.grid(axis="y",color="#eef1f6")

# Ranking empresas por PMPM
ax=panel(fig,0.018,0.022,0.46,0.36,"PMPM por empresa (R$/vida·mês)")
pe=(fato.groupby("empresa_id").custo.sum()/cart.groupby("empresa_id").vidas.sum()).reset_index(name="pmpm").merge(emp,on="empresa_id").sort_values("pmpm")
b=ax.barh(pe.empresa,pe.pmpm,color=[TEAL if v<pe.pmpm.median() else BLUE for v in pe.pmpm],height=0.62)
for r,v in zip(b,pe.pmpm): ax.text(v+3,r.get_y()+r.get_height()/2,brl(v),va="center",fontsize=9,color=NAVY)
ax.set_xlim(0,pe.pmpm.max()*1.18); ax.invert_yaxis(); ax.grid(axis="x",color="#eef1f6")

# Gauge meta sinistralidade
ax=panel(fig,0.49,0.022,0.49,0.36,"Indicador de sinistralidade vs. meta")
ax.set_xlim(-1.2,1.2); ax.set_ylim(-0.2,1.15); ax.axis("off"); ax.set_aspect("equal")
import numpy as np
for a0,a1,col in [(180,180-0.60*180,TEAL),(180-0.60*180,180-0.75*180,AMBER),(180-0.75*180,0,RED)]:
    ax.add_patch(Wedge((0,0),1.0,a1,a0,width=0.30,fc=col,ec="white",lw=1.5))
val=min(sin_glob,1.0); ang=np.radians(180-val*180)
ax.plot([0,0.82*np.cos(ang)],[0,0.82*np.sin(ang)],color=NAVY,lw=3.2)
ax.add_patch(Circle((0,0),0.05,fc=NAVY))
ax.text(0,-0.12,pct(sin_glob),ha="center",fontsize=22,fontweight="bold",color=NAVY)
ax.text(0,0.42,"meta 75%",ha="center",fontsize=10,color=GREY)
ax.text(-1.0,-0.05,"0%",fontsize=8,color=GREY); ax.text(1.0,-0.05,"100%",fontsize=8,color=GREY,ha="right")
fig.savefig(f"{IMG}/painel_3_utilizacao_tendencias.png",facecolor=BG,bbox_inches="tight")
plt.close(fig)
print("Telas geradas em", IMG)
print("Telas OK")
