"""Where does the near miss at height 7005 leave the line? A plain-Python check, no libraries.

Run:  python3 -I tools/check_near_miss_meeting.py     (a few seconds)

The page no_room_to_spare.html quotes the meeting of the two close zeros near height 7005 on the de Bruijn-Newman
dial as t = -0.000711, from Lattice's high-precision tools/check_lehmer_heat.py (which needs mpmath). This file gets
the same number a different way, in ordinary double precision:
  1. zeta on the critical line by Euler-Maclaurin summation, turned into the real wave Z;
  2. a polynomial of degree 16 through that wave (times its smooth envelope) on a window of height 0.7;
  3. the dial run exactly on the polynomial: the heat flow of a polynomial is a finite sum.
It exits with an error if the answer is further than 1e-8 from the high-precision value.
Author: Fixpoint, for Marginalia, 24 November 2026.
"""
import math, cmath, sys
def zeta(s, N):
    tot=sum(n**(-s) for n in range(1,N)); p=N**(-s)
    tot+=p/2+N*p/(s-1)
    B=[1/12,-1/720,1/30240,-1/1209600,1/47900160]; term=s; pw=1/N
    for k in range(1,6):
        tot+=B[k-1]*pw*term*p
        term*= (s+2*k-1)*(s+2*k); pw/=N*N
    return tot
def theta(T): return T/2*math.log(T/(2*math.pi))-T/2-math.pi/8+1/(48*T)+7/(5760*T**3)
def Zc(T, N=7400):
    z=cmath.exp(1j*theta(T))*zeta(complex(0.5,T),N); return z
T0=7005.08; HW=0.35; DEG=16
nodes=[math.cos(math.pi*(k+0.5)/(DEG+1)) for k in range(DEG+1)]
vals=[]; worst_im=0
for u in nodes:
    T=T0+HW*u; z=Zc(T); worst_im=max(worst_im,abs(z.imag))
    # envelope so that the fitted function is H_0 up to a constant: (T^2+1/4) (T/2)^(-1/4) e^(-pi T/4), relative to T0
    env=math.exp(2*math.log(T/T0)-0.25*math.log(T/T0)-math.pi*(T-T0)/4)
    vals.append(z.real*env)
print("largest imaginary part of e^(i theta) zeta at the nodes: %.2e"%worst_im)
# Chebyshev coefficients, then convert to monomials in u (u in [-1,1])
c=[(2/(DEG+1))*sum(vals[k]*math.cos(j*math.pi*(k+0.5)/(DEG+1)) for k in range(DEG+1)) for j in range(DEG+1)]; c[0]/=2
# Chebyshev -> monomial by recurrence
Tk=[[1.0],[0.0,1.0]]
for j in range(2,DEG+1):
    a=[0.0]+[2*x for x in Tk[-1]]; b=Tk[-2]+[0.0]*(len(a)-len(Tk[-2])); Tk.append([x-y for x,y in zip(a,b)])
mono=[0.0]*(DEG+1)
for j in range(DEG+1):
    for i,x in enumerate(Tk[j]): mono[i]+=c[j]*x
# check the fit at fresh points
err=0
for k in range(41):
    u=-0.9+1.8*k/40; T=T0+HW*u; z=Zc(T); env=math.exp(2*math.log(T/T0)-0.25*math.log(T/T0)-math.pi*(T-T0)/4)
    err=max(err,abs(sum(m*u**i for i,m in enumerate(mono))-z.real*env))
print("polynomial of degree %d against fresh values: worst gap %.2e"%(DEG,err))
# dial: H_t = exp(-t d^2/dx^2) H_0 with x = 2T = 2(T0 + HW u): d/dx = (1/(2 HW)) d/du ; so H_t = exp(-tau d^2/du^2) p, tau = t/(4 HW^2)
def flow(t):
    tau=t/(4*HW*HW); out=mono[:]; cur=mono[:]; k=1
    while True:
        cur=[ (i+2)*(i+1)*cur[i+2] for i in range(len(cur)-2)]
        if not cur: break
        f=(-tau)**k/math.factorial(k)
        for i,x in enumerate(cur): out[i]+=f*x
        k+=1
    return out
def P(co,u): return sum(m*u**i for i,m in enumerate(co))
def dP(co,u): return sum(i*m*u**(i-1) for i,m in enumerate(co) if i)
def real_zeros(co,a=-0.5,b=0.5,n=4000):
    out=[]; prev=P(co,a)
    for k in range(1,n+1):
        u=a+(b-a)*k/n; cur=P(co,u)
        if prev*cur<0:
            lo,hi=u-(b-a)/n,u
            for _ in range(60):
                m=(lo+hi)/2
                if P(co,lo)*P(co,m)<=0: hi=m
                else: lo=m
            out.append((lo+hi)/2)
        prev=cur
    return out
z0=real_zeros(flow(0.0)); print("zeros at t = 0 near 7005:", ["%.5f"%(T0+HW*u) for u in z0])
pair=min(((z0[i+1]-z0[i]),z0[i],z0[i+1]) for i in range(len(z0)-1)); gT=pair[0]*HW
print("gap in height %.6f ; rough rule -g^2/8 on the x scale: %.9f"%(gT,-(2*gT)**2/8))
lo,hi=-0.0010,-0.0005
for _ in range(60):
    m=(lo+hi)/2
    zz=[u for u in real_zeros(flow(m)) if pair[1]-0.05<u<pair[2]+0.05]
    if len(zz)>=2: hi=m
    else: lo=m
t=(lo+hi)/2; zz=[u for u in real_zeros(flow(hi)) if pair[1]-0.05<u<pair[2]+0.05]
print("the pair meets at t = %.12f at height %.8f"%(t,T0+HW*(zz[0]+zz[-1])/2))
height=T0+HW*(zz[0]+zz[-1])/2
print("high-precision value: t = -0.000711204733903 at height 7005.08171470549 (tools/check_lehmer_heat.py)")
if abs(t-(-0.000711204733903))>1e-8 or abs(height-7005.08171470549)>1e-6 or worst_im>1e-9 or err>1e-9:
    sys.exit("MISMATCH with the high-precision value, or a check of the fit failed")
print("AGREES to within 1e-8")
