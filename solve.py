#!/usr/bin/env python3
"""solve.py FILE [--deep] [--top N]"""
import itertools, sys, time
from collections import Counter

_report = []
def say(*p):
    line = " ".join(str(x) for x in p)
    print(line); _report.append(line)

NOP,ADD,SQ,OUT,RST,DBL,HLF,NEG,LEFT,RIGHT,PRE = range(11)
BASIC_OPS = {"inc":(ADD,1),"dec":(ADD,-1),"sq":(SQ,0),"out":(OUT,0),
    "reset":(RST,0),"dbl":(DBL,0),"left":(LEFT,0),"right":(RIGHT,0)}
EXTRA_OPS = {"half":(HLF,0),"neg":(NEG,0)}
for _k in (2,3,4,5,8,10,16,32):
    EXTRA_OPS["add%d"%_k]=(ADD,_k); EXTRA_OPS["sub%d"%_k]=(ADD,-_k)
for _k in (2,3,4,5,8,10,16):
    EXTRA_OPS["next_x%d"%_k]=(PRE,_k)
ALL_OPS = dict(BASIC_OPS, **EXTRA_OPS); ALL_OPS["nop"]=(NOP,0)
WRAPS = ("none","deadfish","mod256"); BIG = 10**7

def printable(v): return 32<=v<=126 or v==10

def run(prog, ops, wrap, screen):
    a=0; mult=1; tape={}; ptr=0; out=[]; good=0; since_out=0
    for sym in prog:
        code,arg = ops[sym]
        if code==NOP: continue
        if code==ADD: a+=arg*mult; mult=1
        elif code==OUT:
            out.append(a)
            if screen:
                since_out=0
                if printable(a): good+=1
                n=len(out)
                if n==20 and good<17: return None
                if n==80 and good<72: return None
            continue
        elif code==SQ: a*=a
        elif code==RST: a=0
        elif code==DBL: a*=2
        elif code==HLF: a//=2
        elif code==NEG: a=-a
        elif code==PRE: mult=arg; continue
        elif code in (LEFT,RIGHT):
            tape[ptr]=a; ptr += 1 if code==RIGHT else -1; a=tape.get(ptr,0); continue
        if wrap=="deadfish":
            if a==-1 or a==256: a=0
        elif wrap=="mod256": a&=255
        if screen:
            if a>BIG or a<-BIG: return None
            since_out+=1
            if since_out>6000: return None
    return out

WORDS = """et in est non ad ut cum sed qui quae quod nomen bestia belua piscis
vexillum signum littera litteris minusculis sine spatiis inter hoc haec sunt
monstrum mare maris draco the and flag name beast fish with lowercase is of
submit wrap format underscore""".split()

def to_text(vals): return "".join(chr(v) if printable(v) else "\u00b7" for v in vals)
def word_hits(text):
    low = " " + "".join(c if c.isalpha() else " " for c in text.lower()) + " "
    return sum(low.count(" "+w+" ") for w in WORDS)
def score(vals):
    if len(vals)<8: return 0.0
    n=float(len(vals)); p=sum(1 for v in vals if printable(v))/n
    if p<0.9: return p
    text=to_text(vals); letters=sum(1 for c in text if c.isalpha() or c==" ")/n
    variety=min(1.0,len(set(vals))/12.0); words=min(1.0,word_hits(text)/max(1.0,n/25.0))
    return p+letters*variety+words

def diagnostics(raw, syms, counts):
    say("="*72); say("DIAGNOSTICS"); say("="*72)
    say("bytes:",len(raw)," lines:",raw.count("\n")+1," whitespace:",sum(1 for c in raw if c.isspace()))
    say("symbols by frequency:")
    for s,c in counts.most_common():
        say("   %r  %7d  %5.1f%%"%(s,c,100.0*c/sum(counts.values())))
    body="".join(c for c in raw if not c.isspace())
    total=len(body)
    rare=[s for s in syms if counts[s]<0.1*total]
    return rare

def assignments_basic(syms, rare):
    names=list(BASIC_OPS); others=[x for x in names if x not in ("inc","out")]
    for out_sym in rare:
        for inc_sym in syms:
            if inc_sym==out_sym: continue
            rest=[s for s in syms if s not in (out_sym,inc_sym)]
            for k in range(len(rest)+1):
                for active in itertools.combinations(rest,k):
                    for perm in itertools.permutations(others,k):
                        m={s:"nop" for s in syms}; m[out_sym]="out"; m[inc_sym]="inc"
                        for s,op in zip(active,perm): m[s]=op
                        yield m

def assignments_deep(syms, rare):
    pool=[x for x in ALL_OPS if x not in ("inc","dec","out","nop")]
    for out_sym in rare:
        for inc_sym,dec_sym in itertools.permutations([s for s in syms if s!=out_sym],2):
            rest=[s for s in syms if s not in (out_sym,inc_sym,dec_sym)]
            for k in (1,2):
                for active in itertools.combinations(rest,k):
                    for combo in itertools.product(pool,repeat=k):
                        m={s:"nop" for s in syms}; m[out_sym],m[inc_sym],m[dec_sym]="out","inc","dec"
                        for s,op in zip(active,combo): m[s]=op
                        yield m

def search(label, gen, syms, progs, results):
    say("\nsearching:",label); start=time.time(); tried=0
    for m in gen:
        ops=[ALL_OPS[m[s]] for s in syms]
        for direction,prog in progs:
            for wrap in WRAPS:
                tried+=1
                if run(prog,ops,wrap,True) is None: continue
                vals=run(prog,ops,wrap,False); sc=score(vals)
                if sc>=0.9:
                    key=tuple(vals)
                    if key not in results or results[key][0]<sc:
                        results[key]=(sc,dict(m),wrap,direction)
    say("  tried %d in %.0fs, %d candidates"%(tried,time.time()-start,len(results)))

def show(rank, vals, info, syms):
    sc,m,wrap,direction = info
    text = to_text(vals)
    say("-"*72)
    say("#%d score %.2f wrap=%s source=%s"%(rank,sc,wrap,direction))
    say("    mapping: "+"  ".join("%r=%s"%(s,m[s]) for s in syms))
    say("    TEXT   : "+text)

def main():
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    if not args: print(__doc__); return
    deep="--deep" in sys.argv
    top=15
    if "--top" in sys.argv: top=int(sys.argv[sys.argv.index("--top")+1])
    raw=open(args[0],"r",errors="replace").read()
    body="".join(c for c in raw if not c.isspace())
    counts=Counter(body); syms=[s for s,_ in counts.most_common()]
    rare=diagnostics(raw,syms,counts)
    if len(syms)>8: say("Too many symbols."); 
    elif not rare: say("No rare out symbol.")
    else:
        index={s:i for i,s in enumerate(syms)}
        fwd=[index[c] for c in body]
        progs=[("forward",fwd),("reversed",fwd[::-1])]
        results={}
        search("basic", assignments_basic(syms,rare), syms, progs, results)
        best=max([r[0] for r in results.values()] or [0])
        if deep or best<2.0:
            search("deep", assignments_deep(syms,rare), syms, progs, results)
        ranked=sorted(results.items(), key=lambda kv:-kv[1][0])[:top]
        for rank,(vals,info) in enumerate(ranked,1):
            show(rank,list(vals),info,syms)
    with open("solve_report.txt","w") as fh: fh.write("\n".join(_report)+"\n")
    print("\nsaved to solve_report.txt")

if __name__=="__main__": main()
