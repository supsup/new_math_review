# I3 check (Fixpoint, 2026-11-24). Claim under test, from anthropics/formal-math 11b6c7e eth/README.md:
#   "Per bit, SWAP = I - 2*singlet; grouping by the number of singlets gives lambda+1 operators
#    with (row rank)*(column rank) <= 12^lambda."
# Brute force: build the lambda+1 grouped operators as tensors on four lambda-bit indices (a,b top row; c,d bottom row),
# compute exact ranks across the row cut (a,b | c,d) and the column cut (a,c | b,d), and compare with
#   my closed form  row_j = sum_{k>=j} C(l,k) 3^(l-k),   col_j = sum_{k>=l-j} C(l,k) 3^(l-k)
# and with 12^lambda. Fails if SWAP != sum_j (-1)^j O_j, if a rank differs from the closed form, or if a product exceeds 12^lambda.
import sys, math
from fractions import Fraction
from itertools import product
def e(a,b): return (1 if (a,b)==(0,1) else -1 if (a,b)==(1,0) else 0)
def bits(x,l): return [(x>>i)&1 for i in range(l)]
def grouped(l):
    n=1<<l; O=[dict() for _ in range(l+1)]; ok=True
    for a in range(n):
        A=bits(a,l)
        for b in range(n):
            B=bits(b,l)
            for c in range(n):
                Cc=bits(c,l)
                for d in range(n):
                    Dd=bits(d,l)
                    poly=[1]+[0]*l                      # prod_i (I_i + z E_i), coefficients in z
                    for i in range(l):
                        I=1 if (A[i]==Cc[i] and B[i]==Dd[i]) else 0
                        E=e(A[i],B[i])*e(Cc[i],Dd[i])
                        new=[0]*(l+1)
                        for k,v in enumerate(poly):
                            if v:
                                new[k]+=v*I
                                if k<l: new[k+1]+=v*E
                        poly=new
                    for j,v in enumerate(poly):
                        if v: O[j][(a,b,c,d)]=v
                    swap=1 if (a==d and b==c) else 0
                    if sum((-1)**j*v for j,v in enumerate(poly))!=swap: ok=False
    return O,ok
def rank_mod(rows,p):
    rows=[r[:] for r in rows]; rk=0; ncol=len(rows[0])
    for c in range(ncol):
        q=next((i for i in range(rk,len(rows)) if rows[i][c]%p),None)
        if q is None: continue
        rows[rk],rows[q]=rows[q],rows[rk]; inv=pow(rows[rk][c],-1,p); pr=rows[rk]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]%p:
                f=rows[i][c]*inv%p; ri=rows[i]; rows[i]=[(x-f*y)%p for x,y in zip(ri,pr)]
        rk+=1
    return rk
def rank_Q(rows):
    rows=[[Fraction(v) for v in r] for r in rows]; rk=0
    for c in range(len(rows[0])):
        q=next((i for i in range(rk,len(rows)) if rows[i][c]!=0),None)
        if q is None: continue
        rows[rk],rows[q]=rows[q],rows[rk]; pr=rows[rk]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]!=0:
                f=rows[i][c]/pr[c]; rows[i]=[x-f*y for x,y in zip(rows[i],pr)]
        rk+=1
    return rk
P1,P2=(1<<61)-1,1000003
allok=True
for l in range(1,int(sys.argv[1])+1):
    n=1<<l; O,ok=grouped(l); allok&=ok
    print("lambda=%d  SWAP == sum_j (-1)^j O_j on all %d entries: %s   12^lambda=%d  4^lambda=%d"%(l,n**4,ok,12**l,4**l))
    for j in range(l+1):
        T=O[j]
        rowM=[[T.get((a,b,c,d),0) for c in range(n) for d in range(n)] for a in range(n) for b in range(n)]
        colM=[[T.get((a,b,c,d),0) for b in range(n) for d in range(n)] for a in range(n) for c in range(n)]
        rr=rank_mod(rowM,P1); cr=rank_mod(colM,P1)
        rr2=rank_mod(rowM,P2); cr2=rank_mod(colM,P2)
        exact=""
        if l<=3:
            rq,cq=rank_Q(rowM),rank_Q(colM); exact=" exactQ=(%d,%d)"%(rq,cq);
            if (rq,cq)!=(rr,cr): allok=False
        fr=sum(math.comb(l,k)*3**(l-k) for k in range(j,l+1)); fc=sum(math.comb(l,k)*3**(l-k) for k in range(l-j,l+1))
        good=(rr,cr)==(fr,fc)==(rr2,cr2) and rr*cr<=12**l
        allok&=good
        print("   j=%d  row rank=%d  col rank=%d%s  closed form=(%d,%d)  product=%d  <=12^l: %s  min=%d  (log2 min)/(2*lambda)=%.4f"%(j,rr,cr,exact,fr,fc,rr*cr,rr*cr<=12**l,min(rr,cr),math.log2(min(rr,cr))/(2*l) if min(rr,cr)>0 else 0))
print("ALL CHECKS PASS" if allok else "A CHECK FAILED")
if not allok: sys.exit(1)
print("limit ratio log2(12)/4 = %.4f ; the paper's block count gives 11/12 = %.4f"%(math.log2(12)/4, 11/12))
