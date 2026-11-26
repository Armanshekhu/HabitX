import re, glob, sys
import xml.etree.ElementTree as ET
src = {f: open(f).read() for f in glob.glob('HabitTracker/*.swift')}
allsrc = '\n'.join(src.values())
classes = set(re.findall(r'(?:final )?class (\w+)', allsrc))
errs = 0
def err(m):
    global errs; errs += 1; print('ERR', m)
for sb in ('HabitTracker/Main.storyboard', 'HabitTracker/LaunchScreen.storyboard'):
    tree = ET.parse(sb); root = tree.getroot()
    ids = {}
    for e in root.iter():
        i = e.get('id')
        if i:
            if i in ids: err(f'dup id {i}')
            ids[i] = e
    for e in root.iter():
        for a in ('firstItem', 'secondItem', 'destination'):
            v = e.get(a)
            if v and v not in ids: err(f'{sb}: dangling {a}={v} on <{e.tag}>')
        cc = e.get('customClass')
        if cc and cc not in classes and cc not in ('UIResponder',): err(f'unknown class {cc}')
    # constraint owner sanity: both items must be inside owner view
    parent = {c: p for p in root.iter() for c in p}
    def anc(e):
        out = []
        while e is not None: out.append(e); e = parent.get(e)
        return out
    for con in root.iter('constraint'):
        owner = parent[parent[con]] if parent[con].tag == 'constraints' else None
        owner = parent[con]; owner = parent[owner]  # <constraints> -> view
        for a in ('firstItem', 'secondItem'):
            v = con.get(a)
            if v:
                tgt = ids[v]
                if tgt is not owner and owner not in anc(tgt) and not (tgt.tag == 'viewLayoutGuide'):
                    err(f'{sb}: constraint {con.get("id")} item {v} not within owner')
                if tgt.tag == 'viewLayoutGuide' and owner not in anc(tgt):
                    err(f'{sb}: guide owner mismatch {v}')
    # VC outlets/actions vs Swift
    for vc in root.iter('viewController'):
        cls = vc.get('customClass')
        if not cls: continue
        text = next((t for t in src.values() if re.search(r'class %s\b' % cls, t)), '')
        for o in vc.iter('outlet'):
            p = o.get('property')
            if not re.search(r'@IBOutlet\s+(?:weak\s+)?var\s+%s\b' % p, text): err(f'{cls}: missing outlet {p}')
        for o in vc.iter('outletCollection'):
            p = o.get('property')
            if not re.search(r'@IBOutlet\s+(?:weak\s+)?var\s+%s\b' % p, text): err(f'{cls}: missing outletCollection {p}')
        for o in vc.iter('action'):
            sel = o.get('selector').rstrip(':')
            if not re.search(r'@IBAction\s+func\s+%s\(' % sel, text): err(f'{cls}: missing action {sel}')
        # every Swift outlet connected?
        declared = re.findall(r'@IBOutlet\s+(?:weak\s+)?var\s+(\w+)', text)
        wired = {o.get('property') for o in vc.iter() if o.tag in ('outlet', 'outletCollection')}
        for d in declared:
            if d not in wired: err(f'{cls}: outlet {d} declared but not wired')
    # runtime attribute keypaths on custom classes
    for e in root.iter():
        cc = e.get('customClass')
        if cc in ('HTLabel', 'NavButton', 'ProgressBarView'):
            for ua in e.iter('userDefinedRuntimeAttribute'):
                kp = ua.get('keyPath')
                if not re.search(r'var\s+%s\b' % kp, allsrc): err(f'{cc}: no property {kp}')
    print(sb, 'ids:', len(ids))
print('ERRORS:', errs)
sys.exit(1 if errs else 0)
