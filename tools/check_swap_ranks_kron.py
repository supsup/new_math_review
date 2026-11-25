# Fixpoint, 2026-11-24: a second, faster check of the swap/singlet ranks, used to verify the 4-bit table that a fresh
# agent reported (256,1),(175,13),(67,67),(13,175),(1,256). Each reshaped operator is built bit by bit as a Kronecker
# product of 4 x 4 pieces (rows and columns reordered by bit pairs, which does not change rank); rank is by exact
# elimination modulo two large primes. Independent of check_swap_singlet_ranks.py, which builds the full 4-index tensor.
import sys, math
def e(a,b): return 1 if (a,b)==(0,1) else -1 if (a,b)==(1,0) else 0
PAIRS=[(0,0),(0,1),(1,0),(1,1)]
# per bit: I[a,b,c,d]=[a=c][b=d], E[a,b,c,d]=e(a,b)e(c,d) (= 2P)
I_row=[[1 if (a==c and b==d) else 0 for (c,d) in PAIRS] for (a,b) in PAIRS]      # rows (a,b), columns (c,d)
E_row=[[e(a,b)*e(c,d) for (c,d) in PAIRS] for (a,b) in PAIRS]
I_col=[[1 if (a==c and b==d) else 0 for (b,d) in PAIRS] for (a,c) in PAIRS]      # rows (a,c), columns (b,d)
E_col=[[e(a,b)*e(c,d) for (b,d) in PAIRS] for (a,c) in PAIRS]
def grouped(l, Im, Em):
    n=4**l; mats=[[[0]*n for _ in range(n)] for _ in range(l+1)]
    for r in range(n):
        rd=[(r>>(2*i))&3 for i in range(l)]
        for c in range(n):
            cd=[(c>>(2*i))&3 for i in range(l)]
            poly=[1]+[0]*l
            for i in range(l):
                a,b=Im[rd[i]][cd[i]],Em[rd[i]][cd[i]]; new=[0]*(l+1)
                for k,v in enumerate(poly):
                    if v:
                        new[k]+=v*a
                        if k<l: new[k+1]+=v*b
                poly=new
            for j,v in enumerate(poly):
                if v: mats[j][r][c]=v
    return mats
def rank_mod(rows,p):
    rows=[[v%p for v in r] for r in rows]; rk=0
    for c in range(len(rows[0])):
        q=next((i for i in range(rk,len(rows)) if rows[i][c]),None)
        if q is None: continue
        rows[rk],rows[q]=rows[q],rows[rk]; inv=pow(rows[rk][c],-1,p); pr=rows[rk]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]:
                f=rows[i][c]*inv%p; rows[i]=[(x-f*y)%p for x,y in zip(rows[i],pr)]
        rk+=1
    return rk
ok=True
for l in range(1,int(sys.argv[1])+1):
    R=grouped(l,I_row,E_row); C=grouped(l,I_col,E_col); out=[]
    for j in range(l+1):
        r1,c1=rank_mod(R[j],(1<<61)-1),rank_mod(C[j],(1<<61)-1); r2,c2=rank_mod(R[j],1000003),rank_mod(C[j],1000003)
        fr=sum(math.comb(l,t)*3**(l-t) for t in range(j,l+1)); fc=sum(math.comb(l,k)*3**k for k in range(0,j+1))
        good=(r1,c1)==(r2,c2)==(fr,fc) and r1*c1<=12**l; ok&=good; out.append((r1,c1))
    print("bits=%d"%l, out, "products", [a*b for a,b in out], "12^l =",12**l)
print("ALL MATCH THE FORMULAS" if ok else "MISMATCH")
if not ok: sys.exit(1)
