"""Regenerate FractureAgent figures as vector PDF (polished layout).
Fig6 true heatmap; Fig7 Likert w/ significance + 95% CI (legend outside);
Fig8 ablation (clinical full=4.29); Fig9 failure modes (2/2/3/3/4/8=22);
FigS TCR forest. Output: figures_out/*.pdf (+ png previews)."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt, os
from statsmodels.stats.proportion import proportion_confint
mpl.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"pdf.fonttype":42,
    "axes.spines.top":False,"axes.spines.right":False,"figure.dpi":150,"savefig.bbox":"tight"})
os.makedirs("figures_out",exist_ok=True)
GREEN="#2E8B57"; GRAYS=["#9aa0a6","#b8bcc0","#6b7077","#cfd3d6"]; N=210
wil=lambda p,n=N:[v*100 for v in proportion_confint(round(p*n),n,0.05,"wilson")]

# FIG 6 heatmap
frac=["Distal radius","Proximal humerus","Hip fracture","Tibial plateau","Ankle fracture","Clavicle"]
phase=["Early","Mid","Late"]
M=np.array([[93.2,91.7,94.1],[89.4,91.2,93.5],[90.1,93.8,88.6],[87.3,90.4,91.8],[92.7,93.1,94.2],[88.4,90.7,91.2]])
fig,ax=plt.subplots(figsize=(5.6,4.3)); im=ax.imshow(M,cmap="YlGn",vmin=85,vmax=95,aspect="auto")
ax.set_xticks(range(3)); ax.set_xticklabels(phase); ax.set_yticks(range(6)); ax.set_yticklabels(frac)
for i in range(6):
    for j in range(3):
        ax.text(j,i,f"{M[i,j]:.1f}",ha="center",va="center",color="#143d28" if M[i,j]>90 else "#1b1b1b",fontweight="bold",fontsize=9)
cb=fig.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.set_label("TCR (%)")
ax.set_title("Per-fracture × per-phase task completion rate",fontsize=11,pad=8); ax.set_xlabel("Rehabilitation phase")
fig.text(0.5,-0.03,"Heatmap of Table 4. Per-cell n≈12, so 95% CIs are wide (≈±15 pp); cells should not be ranked finely.",ha="center",fontsize=7.2,style="italic")
fig.savefig("figures_out/Fig6_TCR_heatmap.pdf"); plt.close(fig)

# FIG 7 Likert (legend OUTSIDE right)
dims=["Clinical\naccuracy","Safety","Completeness","Readability","Empathy"]
data={"FractureAgent":[4.31,4.40,4.28,4.05,4.01],"LLaMA-3.1-8B-FT":[3.85,3.78,3.79,3.78,3.75],
      "GPT-4o (5-shot)":[3.87,3.62,3.85,4.05,3.81],"GPT-4o (0-shot)":[3.65,3.48,3.62,3.85,3.45],
      "Qwen3.5 (0-shot)":[3.21,3.10,3.18,3.32,3.24]}
order=list(data); colors={"FractureAgent":GREEN,"LLaMA-3.1-8B-FT":GRAYS[2],"GPT-4o (5-shot)":GRAYS[0],"GPT-4o (0-shot)":GRAYS[1],"Qwen3.5 (0-shot)":GRAYS[3]}
err=0.48/np.sqrt(60)*1.96; fig,ax=plt.subplots(figsize=(7.8,4.6)); nb=len(order); h=0.15; y=np.arange(len(dims))
for bi,m in enumerate(order):
    ax.barh(y+(bi-(nb-1)/2)*h,data[m],height=h,color=colors[m],xerr=err,error_kw=dict(lw=0.7,ecolor="#555",capsize=1.5),label=m,zorder=3)
for di,sg in {0:"***",1:"**",2:"***"}.items():
    ax.text(4.6,y[di]-(nb-1)/2*h,sg,va="center",fontsize=10,color=GREEN,fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels(dims); ax.invert_yaxis(); ax.set_xlim(2.5,4.75)
ax.set_xlabel("Mean expert Likert rating (1–5)"); ax.set_title("Per-dimension expert ratings (n=6 raters; ICC=0.83)",fontsize=11)
ax.legend(fontsize=7.8,loc="center left",bbox_to_anchor=(1.01,0.5),frameon=False)
fig.text(0.012,-0.02,"Error bars: representative 95% CI (SD 0.48, n=60).  *** p<0.001, ** p<0.01 (FractureAgent vs all baselines, ANOVA+Tukey).",fontsize=6.9,style="italic")
fig.savefig("figures_out/Fig7_Likert_dimensions.pdf"); plt.close(fig)

# FIG 8 ablation (clinical full -> 4.29)
cfg=["Full","w/o exercise_query","w/o pain_assess","w/o progress_track","w/o literature_search","w/o fine-tuning"]
tcr=[91.4,76.2,82.7,85.3,88.1,61.4]; sens=[0.843,0.841,0.601,0.838,0.840,0.592]; clin=[4.29,3.63,3.91,3.87,3.94,3.21]
x=np.arange(len(cfg)); w=0.26; fig,ax=plt.subplots(figsize=(7.8,4.5))
ax.bar(x-w,tcr,w,color=GREEN,label="TCR (%)",zorder=3); ax.bar(x,[c*20 for c in clin],w,color="#E1A140",label="Clinical ×20",zorder=3)
ax.bar(x+w,[s*100 for s in sens],w,color="#7B5EA7",label="Complic. sens. ×100",zorder=3)
for i,tv in enumerate(tcr): ax.text(i-w,tv+1,f"{tv-91.4:+.1f}" if i else "ref",ha="center",fontsize=7.2,color="#143d28")
ax.set_xticks(x); ax.set_xticklabels(cfg,rotation=20,ha="right",fontsize=8); ax.set_ylabel("Score (rescaled)"); ax.set_ylim(0,100)
ax.set_title("Ablation — removing each component (ΔTCR vs full above bars)",fontsize=11); ax.legend(fontsize=8,frameon=False,loc="lower left")
fig.savefig("figures_out/Fig8_ablation.pdf"); plt.close(fig)

# FIG 9 failure modes (corrected counts, total 22)
cats=["Wrong tool\nselected","Tool args\nmalformed","Hallucinated\nexercise","Missed\nescalation cue","Over-conservative\nescalation","Off-topic /\nrefusal"]
cnt=[8,4,3,3,2,2]; cols=["#3a6f52","#5b8c6e","#E1A140","#C0552B","#7B5EA7","#9aa0a6"]
fig,(a1,a2)=plt.subplots(1,2,figsize=(9.2,4.3),gridspec_kw={"width_ratios":[1,1.25]})
wed,_,aut=a1.pie(cnt,colors=cols,autopct=lambda p:f"{p*22/100:.0f}",startangle=90,counterclock=False,
                 wedgeprops=dict(width=0.45,edgecolor="white"),pctdistance=0.78,textprops=dict(fontsize=9,color="white",fontweight="bold"))
a1.set_title("Failure categories (n = 22 of 210, 10.5%)",fontsize=10)
yb=np.arange(len(cats))[::-1]; a2.barh(yb,cnt,color=cols,zorder=3)
for yv,c in zip(yb,cnt): a2.text(c+0.12,yv,str(c),va="center",fontsize=9,fontweight="bold")
a2.set_yticks(yb); a2.set_yticklabels([c.replace("\n"," ") for c in cats],fontsize=8.5); a2.set_xlim(0,9)
a2.set_xlabel("Number of failed scenarios"); a2.set_title("Tool-orchestration errors (8+4=12/22) dominate",fontsize=9.5)
fig.suptitle("Failure-mode breakdown across the 22 failed scenarios",fontsize=11,y=1.02)
fig.savefig("figures_out/Fig9_failure_modes.pdf"); plt.close(fig)

# FIG S forest (TCR unchanged)
models=["FractureAgent","LLaMA-3.1-8B-FT","GPT-4o (5-shot)","GPT-4o (0-shot)","Qwen3.5-9B (base)","Static rule-based"]; pts=[91.4,79.5,73.8,67.3,61.4,52.4]
fig,ax=plt.subplots(figsize=(6.8,3.7))
for i,(m,p) in enumerate(zip(models,pts)):
    lo,hi=wil(p/100); c=GREEN if m=="FractureAgent" else "#5b6166"
    ax.plot([lo,hi],[i,i],color=c,lw=2,zorder=2); ax.plot(p,i,"o",color=c,ms=7,zorder=3)
    ax.text(hi+0.8,i,f"{p:.1f}  [{lo:.1f}, {hi:.1f}]",va="center",fontsize=8,color=c)
ax.set_yticks(range(len(models))); ax.set_yticklabels(models); ax.invert_yaxis(); ax.set_xlim(40,104)
ax.set_xlabel("Task completion rate (%) with Wilson 95% CI  (n=210)"); ax.set_title("TCR with 95% confidence intervals",fontsize=11)
ax.axvline(91.4,color=GREEN,ls=":",lw=0.8,zorder=1); fig.savefig("figures_out/FigS_TCR_forest.pdf"); plt.close(fig)
print("figures regenerated:", sorted(os.listdir("figures_out")))
