
#!/usr/bin/python
from __future__ import print_function
import numpy as np
import pandas as pd
import os,sys,csv,random,math,pickle,re,string,glob,gzip
import collections
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none' # or svgfont?
import seaborn as sns
import multiprocessing as mp
from Bio import SeqIO, bgzf
from Bio.Seq import Seq
from scipy.stats import ttest_ind, t,pearsonr,spearmanr
import screenlib as sl
import fastqlib as fl
import qplot as qplt
import qslib as ql
cr=qplt.brewer(n=9,set=1)
mk=qplt.markers()
cmap0='viridis'



# # 1 *** install required packages, e.g pandas, biopython; 



ncore=6
ow=0 # overwriting existing..
# *********############

libf1='HLAcP_v2BC' # for R1 reads- HLA barcodes here. contains columns: name (HLA alleles) and HLAbc (barcodes for HLA)
plib1=pd.read_csv(libf1+'.csv',sep=",") # 
#brulib=pd.read_excel(libf,sheet_name='mix2')
hName1=plib1['name'].tolist() # HLA names
hSeq1=plib1['HLAbc'].values.tolist()
print('HLA count:',len(list(set(hSeq1))),len(hSeq1))


libf2='neo_pHLA2' # for R2 reads.. HLA peptides here. 
#affi='HLApool1A'
plib2=pd.read_csv(libf2+'.csv',sep=",") # 
pName2=plib2['name'].tolist() # peptide gene-mutation name
pSeq2=plib2['Seq'].values.tolist()
AA=[str(Seq(k).translate()) for k in pSeq2]
plib2['AA']=AA
print('pHLA count',len(list(set(plib2['Seq']))),len(plib2['Seq']))

print(plib2[plib2.duplicated(subset=['Seq','AA'],keep='last')])


if step==1: 
# extract peptide/guide from fastq files. 
#groups reads by conditions/replicates: per label here. 

### extract hla barcodes...
	dir0='./fq1025b/'#'./L418plasmid/' # directory folder with fastq files..
	fname0='L471' # file naming..
	# here process all files, no subfolders
	f0=''
	seed='TCGATCCCACTT' #HLA barcode: HLA peptide SP: 'GAGGGCTCGGCA'#'CCACCTTGTTG' # before sgRNA  mU6..
	ends='ACGG' # HLA barcode end R1; 
	#files=glob.glob(dir0+'*R1_001.fastq.gz') 

	# reads R2
	seed2='GAGGGCTCGGCA'#'CCACCTTGTTG' # before sgRNA  mU6..
	ends2='GGATGCGGA' # no cys version; #'GGATGCGGA' ; no cys: GGAGGCGGA

	files=glob.glob(dir0+f0+'*_R1_001.fastq.gz') # I7 with b2m barcodes...
	dataset1=[os.path.splitext(os.path.splitext(os.path.basename(k))[0])[0] for k in files]
	labels=list(set([k.split('_')[0] for k in dataset1]))
	print('labels:',labels)
	sample=labels[0].split('-')[0] # sample name
	for la in labels:
		glist0=[]
		files=glob.glob(dir0+f0+la+'*_R1_001.fastq.gz')
		for k0 in files:
			k=os.path.splitext(os.path.splitext(k0)[0])[0]
			print('extract guide of ', k)
			out=sl.fq2extract(k,start=seed,ow=ow,len=42,end=ends) # list as output..
			glist0.extend(out)
		print('extract guides total:',len(glist0))
		# mape guides to master table. 
		ow2=ow
		fn=dir0+f0+la+'_R1_sgRNA'
		glist1=[str(Seq(k).reverse_complement()) for k in glist0]
		# index list
		lidx=sl.map_guides_ord(glist1,sgRNA=hSeq1,genes=hName1,ow=ow2,save=1,fname=fn,mp=1,ncore=ncore)

		# parse R2: pHLA..
		glist2=[]
		files2=[k.replace('_R1_','_R2_') for k in files]
		for k2 in files2:
			k=os.path.splitext(os.path.splitext(k2)[0])[0]
			print('extract guide of ', k)
			out=sl.fq2extract(k,start=seed2,ow=ow,len=42,end=ends2)
			glist2.extend(out)
		print('with total extracted of:',len(glist2))
		# mape guides to master table. 
		ow2=ow
		fn=dir0+f0+la+'_R2_sgRNA'
		lidx2=sl.map_guides_ord(glist2,sgRNA=pSeq2,genes=pName2,ow=ow2,save=1,fname=fn,mp=1,ncore=ncore)

		# build count matrix.. pHLA rows and HLA columns..
		mat=np.zeros((len(pSeq2),len(hSeq1)))
		print(mat.shape,len(lidx),len(lidx2))
		for bc,pep in zip(lidx,lidx2): # R1/hla, R2:pHLA
			if bc>=0 and pep>=0:
				mat[pep,bc]+=1
		fn2=dir0+f0+la
		with open(fn2+'_MatIdx.pickle','wb') as f: # 'wb in py3', 'w' in py2
			pickle.dump([mat,lidx2,lidx],f) # record matrix, index list for R2 and R1.. 


# reading all the pickle files and fill the matrix/datagrame: 
# peptide DNA, peptide-AA, HLA, HLA-bc;  
def Name2num(df,**kwargs):
	# input dataframe, with name column, extract number by _num; output: list of numbers
	lis0=df['name'].tolist()
	return(np.array([int(c.split('_')[-1]) for c in lis0]))

wt=[0,2.0,4.0,8.0] # weight for each sorted fraction.
cs=wt[3]/2*0.9 # cutoff for score. 
cs_af=0.4256252 # cut off affinity to 500nM
ct_cutoff=40 # read count cutoff if lower than this number

if step==2: 
	# merge count table 
	folders=['fq1012','fq1019','fq1025b']
	#folders=['hiseq1']
	names=['BG1','BG2','Lo1','Lo2','M1','M2','H1','H2','R1','R2']
	f2='L471'
	mat=[] # list of matrix per lib..

	fn=f2+'_Mat.pickle'
	if os.path.isfile(fn):
		print('alread existed, loading- ',fn)
		with open(fn,'rb') as f:
			mat=pickle.load(f)
			print('total count per group kb: ',[int(c.sum()/1000) for c in mat])
	else:
		for n in range(len(names)): # go over each matrix...
			m0=np.zeros((len(pSeq2),len(hSeq1)))
			for k in folders:
				f1='./'+k+'/'+f2+names[n]+'_MatIdx'
				if os.path.isfile(f1+'.pickle'):
					print('loading file: ',f1,m0.max())
					with open(f1+'.pickle','rb') as f:
						mat0,lidx2,lidx=pickle.load(f)
						m0=m0+mat0 # numpy array
				else:
					print('file not exist!',f1)
			mat.append(m0)
			print('all reads count for',n,m0.sum())
		with open(f2+'_Mat.pickle','wb') as f: # 'wb in py3', 'w' in py2
			pickle.dump(mat,f) # record matrix, index list for R2 and R1..
		print('total count per group in kb: ',[int(d.sum()/1000) for d in mat])

if step==3:
	# check some stuff. 
	#names=['BG2','Lo1','Lo2','M1','M2','H1','H2','BG1']
	names=['BG1','BG2','Lo1','Lo2','M1','M2','H1','H2','R1','R2']
	mat=[]
	f2='L471'
	fn=f2+'_Mat.pickle'
	if os.path.isfile(fn):
		print('alread existed, loading- ',fn)
		with open(fn,'rb') as f:
			mat=pickle.load(f)
			print('total count: ',sum([c.sum() for c in mat]))
	# load matrix
	BG1=mat[names.index('BG1')]
	BG2=mat[names.index('BG2')]
	M1=mat[names.index('M1')]
	M2=mat[names.index('M2')]
	H1=mat[names.index('H1')]
	H2=mat[names.index('H2')]
	Lo1=mat[names.index('Lo1')]
	Lo2=mat[names.index('Lo2')]
	R1=mat[names.index('R1')]
	R2=mat[names.index('R2')]

	BG1n=BG1*10000000.0/BG1.sum()
	BG2n=BG2*10000000.0/BG2.sum()
	Lo1n=Lo1*10000000.0/Lo1.sum()
	Lo2n=Lo2*10000000.0/Lo2.sum()
	M1n=M1*10000000.0/M1.sum()
	M2n=M2*10000000.0/M2.sum()
	H1n=H1*10000000.0/H1.sum()
	H2n=H2*10000000.0/H2.sum()
	sum1=BG1+Lo1+M1+H1
	sum2=BG2+Lo2+M2+H2
	mask=np.logical_and(sum1>=ct_cutoff,sum2>=ct_cutoff) # or & ; 1 is good. 
	print('good peptide count',sum(mask))
	# calculate the score: 
	ms1=np.asarray((wt[0]*BG1n+wt[1]*Lo1n+wt[2]*M1n+wt[3]*H1n)/(BG1n+Lo1n+M1n+H1n+0.01))
	ms2=np.asarray((wt[0]*BG2n+wt[1]*Lo2n+wt[2]*M2n+wt[3]*H2n)/(BG2n+Lo2n+M2n+H2n+0.01))
	
	with open(f2+'_SMat.pickle','wb') as f: # 'wb in py3', 'w' in py2
		pickle.dump([['score1','score2','mask'],[ms1,ms2,mask]],f) # record matrix, index list for R2 and R1..

# for normalization..
normco=4.0 # cutoff for normalization..
dx=0.04 # delta x for serach for peak etc. 
base=2 # center on after normalziation..
cs=4 # score cutoff.. as positive vs not..
hlact=[14,29,7] # a, b, c
if step==4: # using api/weblink based to get NetMHC score and parse the data into matrix..
	f2='L471'
	fn=f2+'_SMat.pickle'
	if os.path.isfile(fn):
		print('alread existed, loading- ',fn)
		with open(fn,'rb') as f:
			name1,mat=pickle.load(f,encoding="latin1") # name, matrix, list of.. ms1, mscore2, mask
	net='netmhcpan_preds.csv'
	dfnet=pd.read_csv(net,sep=',')
	mat_ic50=10000+np.zeros((len(pSeq2),len(hSeq1)))
	mat_elrank=100+np.zeros((len(pSeq2),len(hSeq1)))

	mask=mat[2]
	hlas=dfnet['allele'].tolist()
	pep=dfnet['peptide'].tolist()
	ic50ba=dfnet['ic50_ba'].tolist()
	rankel=dfnet['percentile_rank_el'].tolist()

	for k in range(len(pep)): # fill each peptide data to matrix.
		hla=hlas[k].split('-')[1]
		idx=[i0 for i0, x in enumerate(AA) if x==pep[k] ]
		for c in idx:
			mat_ic50[c,hName1.index(hla)]=ic50ba[k]
			mat_elrank[c,hName1.index(hla)]=rankel[k]
	#print(mat_ic50,mat_elrank)
	# parse the mutation, wt peptide info etc.
	print('row score max:',mat[0].max(axis=1), len(mat[0].max(axis=1)))

	# with open(f2+'_SMat2.pickle','wb') as f: # 'wb in py3', 'w' in py2
	# 	pickle.dump([name1+['ic50','rankel'],mat+[mat_ic50,mat_elrank]],f) # record matrix, index list for R2 and R1..
	pd.DataFrame(mat_ic50,columns=hName1).to_csv(f2+'_NetIC50.csv')	
	#pd.DataFrame(mat_elrank,columns=hName1).to_csv(f2+'_NetRank.csv')	

def mutparser(n1,**kwargs):
	# parse the name as in RASG12 (already removed last mutation AA): gene+amino acid+position+mutant. 
	if not n1[-1].isdigit(): print('not mutation!'); return()
	m=re.search(r'\d+$',n1) # multitple digits d+, from end ($)
	pos=m.group()
	AAwt=n1[-(len(str(pos))+1)]
	return([n1[:-(len(str(pos))+1)],AAwt,pos]) # [gene_name, wt_AA, pos]

def nameparser(name1,**kwargs):
	# parse name xxx_n, output a list of: 
	#gene(-seperated), mut/annotation,mutation-pos, scan_pos(0-8)/4, kinds:mut/fusion/wt/other(m/f/w/o),wt-AA, mut_AA/7
	# if fusion: 
	al=name1.split('_') 
	
	if len(al)==2: # mutation..
		scan_pos=al[1]
		if al[0][-1].isdigit():# G12, then wt
			kinds='w'
			muts=mutparser(al[0]) # gene_name, wt_AA, Apos
			return([muts[0],muts[1]+str(muts[2]),muts[2],scan_pos,kinds,muts[1],''])
		else: # a letter, mutation..
			kinds='m'
			muts=mutparser(al[0][:-1]) # gene_name, wt_AA, Apos
			return([muts[0],muts[1]+str(muts[2])+al[0][-1],muts[2],scan_pos,kinds,muts[1],al[0][-1]])
		#gene(-seperated), mut/annotation,mutation-pos, scan_pos(0-8)/4, kinds:mut/fusion/wt/other(m/f/w/o),wt-AA, mut_AA/7
	elif al[1]=='N': # N AA variants case. 
		kinds='o'
		mut=al[2]
		return(al[0],al[2],mut[1:-1],al[-1],kinds,mut[0],mut[-1])
	elif int(re.sub("[^0-9]","",al[1]))>20: # fusion: gene1_pos_gene2+pos2_scanpos
		kinds='f'
		gene2=al[2].rstrip('0123456789')
		return([al[0],gene2,al[1],al[3],kinds,'','']) # gene1,gene2,pos1,scan-pos,kinds,'',''
	elif len(al)%2==0: # in pairs: genemut_scanpos
		scan_pos=al[1]
		mutAA=''
		geneli=[] # gene list
		mutli=[]# mut list
		for k in range(int(len(al)/2)): # go over each pairs. 			
			cue=al[2*k] # current element. 			
			if cue[-1].isdigit():# G12, then wt
				kinds='w'
				muts=mutparser(cue) # gene_name, wt_AA, Apos
				geneli.append(muts[0])
				mutli.append(muts[1]+str(muts[2]))
			else: # a letter, mutation..
				kinds='m'
				muts=mutparser(cue[:-1]) # gene_name, wt_AA, Apos
				geneli.append(muts[0])
				mutli.append(muts[1]+str(muts[2])+cue[-1])
				mutAA=cue[-1]
		return(['-'.join(geneli),'-'.join(mutli),muts[2],scan_pos,kinds,muts[1],mutAA])
	else:
		print('none of above situation, check sth wrong?',name1); return()
cs=3.8
f2='L471'
if step==5: 
	# read list of matrix now; and create a df for score, across HLAs, then various columns for plotting..

	fn=f2+'_SMat2.pickle'
	if os.path.isfile(fn):
		print('alread existed, loading- ',fn)
		with open(fn,'rb') as f:
			name1,mat=pickle.load(f,encoding='latin1') # name, matrix, list of.. score1,score2,mask, ic50,rankel.
	s1=mat[0]
	s2=mat[1]
	mask=mat[2]
	pr1=np.zeros(len(hName1)) # HLA names? positive rates..
	pr2=np.zeros(len(hName1))
	score0=1.0*(s1+s2)/2 # not corrected scores.
	cos=[]# cutoff score list
	for k in range(len(hName1)):
		s10=s1[:,k]
		s20=s2[:,k]
		mod1=ql.mode(s10[s10<=normco],dx=dx) # mode/peak, and width..
		mod2=ql.mode(s20[s20<=normco],dx=dx)
		s1[:,k]=s1[:,k]-mod1[0]+base # normalized to..
		s2[:,k]=s2[:,k]-mod2[0]+base # normalized to..
		pr1[k]=100.0*np.sum(s1[:,k]>=cs)/np.sum(s1[:,k]>0)
		pr2[k]=100.0*np.sum(s2[:,k]>=cs)/np.sum(s2[:,k]>0)

	score1=1.0*(s1+s2)/2 # corrected score..
	df1=pd.DataFrame(score1,index=pName2,columns=hName1)
	df10=pd.DataFrame(score0,index=pName2,columns=hName1)
	print(df1.shape,len(AA))
	df1['name']=pName2
	df1['AA']=AA # peptide seq;
	df10['name']=pName2
	df10['AA']=AA # peptide seq;

	bl_pp=(s1.max(axis=1)>cs)&(s2.max(axis=1)>cs) # peptide with at least one positive.. boolean or mask for rows..
	maskr=(mask.max(axis=1)>0)
	matadd=[] # matrix to be added.. with columns: 
	#gene(-seperated), mut/annotation,mutation-pos, scan_pos(0-8)/4, kinds:mut/fusion/wt/other(m/f/w/o),wt-AA, mut_AA/7
	for k in pName2: # parse variuos info about the peptide/gene etc. 
		res=nameparser(k)
		if len(res)!=7:print('something wrong, check,',k)
		matadd.append(res)
	dfa=pd.DataFrame(data=np.array(matadd),index=pName2,columns=['gene','mutation','mpos','spos','kind','wt_AA','mut_AA'])
	print(dfa.shape,df1.shape,df1.columns)
	df2=pd.concat([df1,dfa],axis=1)
	df20=pd.concat([df10,dfa],axis=1)
	df2['mask']=maskr # not non-presented. 
	df2['goodp']=bl_pp #both score above threshold..

	#df2.drop(df2[df2['mut_AA']=='X'].index,inplace=True)
	#print(df2)
	# geneS12V_num/pos; fusion: x_num_y_num_pos/AA; some combo with multile gene. 
	# add wt peptide information;  a matrix...?
	# neoantigen column  1/0 a matrix..
	scorewt=df2.copy(deep=True)
	neoantigen=df2.copy(deep=True)
	kinds=df2['kind'].tolist()
	for k in range(len(pName2)): # go over each peptide
		name=pName2[k]
		if kinds[k]!='m':continue
		kn=name.split('_')
		newN='_'.join([kn[0][:-1],kn[1]]) # wt peptide name
		dfx=df2.loc[df2['name'].str.contains(newN)]
		#print(dfx)
		if len(dfx.index)==1:
			#print(len(scorewt.iloc[k,:]),len(dfx.iloc[:,:].values.flatten().tolist()))
			scorewt.iloc[k,:]=dfx.iloc[:,:].values.flatten().tolist()
		else:
			print('found multiple, check',dfx)

	# # (***** write to files..______-------------)
	# with open(f2+'_SMat_norm.pickle','wb') as f: # 'wb in py3', 'w' in py2
	# # normalized score matrix. 
	# 	pickle.dump([name1,[s1,s2]+mat[2:]],f) # record matrix, index list for R2 and R1..

	#scorewt.to_csv(f2+'_wtscore.csv')	
	#df2.to_csv(f2+'_score.csv')
	#df20.to_csv(f2+'_score0.csv') # score with no correction..



