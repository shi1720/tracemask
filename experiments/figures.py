import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from tracemask import Automaton,StreamMask
root=Path(__file__).resolve().parents[1]
out=root/'paper/figures'; out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':240})
colors={'earliest':'#176b87','suffix':'#679c46','fixed_safe':'#cb6c32','full':'#7866a4'}
rows=list(csv.DictReader((root/'results/trials.csv').open()))
fig,axs=plt.subplots(1,2,figsize=(10.2,3.4),sharey=True)
for ax,kind in zip(axs,['identifier','phrase']):
 for mode in ['earliest','suffix','fixed_safe','full']:
  vals=[np.mean([float(r['mean_delay']) for r in rows if r['kind']==kind and r['method']==mode and int(r['length'])==n]) for n in [16,32,64,128,256]]
  ax.plot([16,32,64,128,256],vals,marker='o',ms=4,color=colors[mode],label={'earliest':'TraceMask','suffix':'Suffix holdback','fixed_safe':'Fixed L-1','full':'Full response'}[mode])
 ax.set_xscale('log',base=2); ax.set_xticks([16,32,64,128,256],labels=[16,32,64,128,256]);ax.set_title(kind.capitalize()+' literals');ax.set_xlabel('Registered secret length (code points)');ax.grid(alpha=.2)
axs[0].set_ylabel('Mean added filter delay (input code points)')
axs[1].legend(frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(out/'delay_by_length.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.7,3.5))
for mode in ['earliest','suffix','fixed_safe','full']:
 v=sorted(np.mean([float(r['mean_delay']) for r in rows if r['method']==mode and int(r['id'])==i]) for i in range(400))
 ax.plot(v,np.arange(1,401)/400,label={'earliest':'TraceMask','suffix':'Suffix holdback','fixed_safe':'Fixed L-1','full':'Full response'}[mode],color=colors[mode],lw=1.8)
ax.set_xlabel('Document mean added filter delay (input code points)');ax.set_ylabel('Fraction of documents');ax.legend(frameon=False);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'delay_cdf.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(10.2,2.8));ax.set_xlim(0,10.2);ax.set_ylim(0,2.8);ax.axis('off')
boxes=[(.05,1.1,1.85,'UTF-8 bytes','incremental decoder'),(2.6,1.1,2.05,'SSE events','strict delta schema'),(5.35,1.1,2.15,'Literal decisions','AC + release frontier'),(8.2,1.1,1.9,'Released text','client / log / TTS')]
for x,y,w,title,sub in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,.95,boxstyle='round,pad=0.03',facecolor='#edf4f7',edgecolor='#176b87'))
 ax.text(x+w/2,y+.61,title,ha='center',va='center',weight='bold',fontsize=10)
 ax.text(x+w/2,y+.26,sub,ha='center',va='center',fontsize=8.5)
for x1,x2 in [(1.96,2.52),(4.72,5.27),(7.57,8.12)]:ax.annotate('',xy=(x2,1.57),xytext=(x1,1.57),arrowprops={'arrowstyle':'->','color':'#176b87','lw':1.5})
ax.text(5.1,2.48,'One policy snapshot and one matcher state per logical stream',ha='center',fontsize=11)
ax.text(5.1,.63,'Application done: flush determined final tail',ha='center',color='#34672d',fontsize=10)
ax.text(5.1,.20,'Disconnect / cancellation / malformed event: discard unresolved tail',ha='center',color='#a44231',fontsize=10)
fig.tight_layout();fig.savefig(out/'gateway.png');plt.close(fig)
# Mechanism construction: prefix-related literals can leave no unresolved text.
fig,axs=plt.subplots(1,2,figsize=(10.2,3.2))
for ax,pats,title in zip(axs,[['a'*16],['a','a'*15+'b']],['One unresolved long literal','Every observed character already covered']):
 for mode in ['earliest','suffix','fixed']:
  s=StreamMask(Automaton(pats),mode=mode,lag=15);pending=[]
  for i in range(48):s.push('a');pending.append(len(s.pending))
  ax.plot(range(1,49),pending,label={'earliest':'TraceMask','suffix':'Suffix holdback','fixed':'Fixed L-1'}[mode],color=colors.get(mode,colors['fixed_safe']),linestyle={'earliest':'-','suffix':'--','fixed':':' }[mode],lw=2)
 ax.set_title(title,fontsize=10);ax.set_xlabel('Received code points');ax.set_ylim(-1,17);ax.grid(alpha=.2)
axs[0].set_ylabel('Unreleased code points');axs[1].legend(frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(out/'pending_bounds.png');plt.close(fig)
print('Four figures written to',out)
