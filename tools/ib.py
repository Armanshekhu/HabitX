"""Tiny Interface Builder XML writer (UIKit storyboards) with auto-resolved constraint owners."""
import random
_rng = random.Random(20261124)
_used = set()
_alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
def new_id():
    while True:
        s = ''.join(_rng.choice(_alpha) for _ in range(3)) + '-' + ''.join(_rng.choice(_alpha) for _ in range(2)) + '-' + ''.join(_rng.choice(_alpha) for _ in range(3))
        if s not in _used:
            _used.add(s); return s

def f(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return s if s else '0'

def color(key, hexv, alpha=1.0):
    r, g, b = (hexv >> 16) & 255, (hexv >> 8) & 255, hexv & 255
    return (f'<color key="{key}" red="{r/255:.9f}" green="{g/255:.9f}" blue="{b/255:.9f}" '
            f'alpha="{alpha}" colorSpace="custom" customColorSpace="sRGB"/>')

def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

WEIGHTS = {400: None, 500: 'medium', 600: 'semibold', 700: 'bold', 800: 'heavy'}
def font(size, w=400):
    wt = WEIGHTS[w]
    return f'<fontDescription key="fontDescription" type="system"' + (f' weight="{wt}"' if wt else '') + f' pointSize="{size}"/>'

class Guide:
    def __init__(self, owner, key):
        self.id = new_id(); self.owner = owner; self.key = key

class Node:
    def __init__(self, kind, frame, **a):
        self.kind = kind; self.frame = frame; self.a = a
        self.id = new_id(); self.parent = None; self.children = []; self.cons = []
        self.guides = []
    def add(self, *kids):
        for k in kids:
            k.parent = self; self.children.append(k)
        return self
    def guide(self, key):
        g = Guide(self, key); self.guides.append(g); return g

def _node_of(x):
    return x.owner if isinstance(x, Guide) else x
def _chain(n):
    out = []
    while n is not None:
        out.append(n); n = n.parent
    return out

class Scene:
    def __init__(self, vc_class, root, tag='viewController'):
        self.vc_class = vc_class; self.root = root; self.id = new_id(); self.sid = new_id()
        self.rootid = root.id; self.outlets = []; self.collections = []; self.cons = []
        self.tag = tag
    def con(self, first, fa, second=None, sa=None, c=0, rel=None, mult=None, prio=None):
        self.cons.append(dict(first=first, fa=fa, second=second, sa=sa, c=c, rel=rel, mult=mult, prio=prio, id=new_id()))
    def finalize(self):
        for k in self.cons:
            if k['second'] is None:
                _node_of(k['first']).cons.append(k)
            else:
                a, b = _chain(_node_of(k['first'])), _chain(_node_of(k['second']))
                owner = next(n for n in a if n in b)
                owner.cons.append(k)

def con_xml(k):
    s = '<constraint'
    if k['second'] is not None or isinstance(k['first'], Guide):
        s += f' firstItem="{k["first"].id}"'
    elif k['second'] is None and False:
        pass
    s += f' firstAttribute="{k["fa"]}"'
    if k['rel']: s += f' relation="{k["rel"]}"'
    if k['second'] is not None:
        s += f' secondItem="{k["second"].id}" secondAttribute="{k["sa"]}"'
    if k['mult'] is not None: s += f' multiplier="{k["mult"]}"'
    if k['c']: s += f' constant="{f(k["c"])}"'
    if k['prio']: s += f' priority="{k["prio"]}"'
    return s + f' id="{k["id"]}"/>'

def rect(n):
    x, y, w, h = n.frame
    return f'<rect key="frame" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/>'

def cls_attrs(a):
    if a.get('cls'):
        return f' customClass="{a["cls"]}" customModule="HabitTracker" customModuleProvider="target"'
    return ''

def runtime(a):
    rt = a.get('rt')
    if not rt: return ''
    out = ['<userDefinedRuntimeAttributes>']
    for kp, typ, val in rt:
        if typ == 'string':
            out.append(f'<userDefinedRuntimeAttribute type="string" keyPath="{kp}" value="{esc(val)}"/>')
        elif typ == 'int':
            out.append(f'<userDefinedRuntimeAttribute type="number" keyPath="{kp}"><integer key="value" value="{val}"/></userDefinedRuntimeAttribute>')
        elif typ == 'real':
            out.append(f'<userDefinedRuntimeAttribute type="number" keyPath="{kp}"><real key="value" value="{val}"/></userDefinedRuntimeAttribute>')
    out.append('</userDefinedRuntimeAttributes>')
    return '\n'.join(out)

def cons_block(n):
    if not n.cons: return ''
    return '<constraints>\n' + '\n'.join(con_xml(k) for k in n.cons) + '\n</constraints>'

def kids_block(n):
    if not n.children: return ''
    return '<subviews>\n' + '\n'.join(render(c) for c in n.children) + '\n</subviews>'

def connections(n, scene_ids):
    items = []
    for sel in n.a.get('actions', []):
        items.append(f'<action selector="{sel}" destination="{scene_ids["vc"]}" eventType="touchUpInside" id="{new_id()}"/>')
    sg = n.a.get('segue')
    if sg:
        dest, ident = sg
        items.append(f'<segue destination="{dest}" kind="show" identifier="{ident}" id="{new_id()}"/>')
    if not items: return ''
    return '<connections>\n' + '\n'.join(items) + '\n</connections>'

_CURRENT = {}
def render(n):
    a = n.a; k = n.kind
    bg = color('backgroundColor', a['bg'], a.get('bga', 1.0)) if 'bg' in a else ''
    if k == 'label':
        attrs = (f'opaque="NO" userInteractionEnabled="NO" contentMode="left" horizontalHuggingPriority="251" verticalHuggingPriority="251" '
                 f'text="{esc(a["text"])}" textAlignment="{a.get("align", "natural")}" lineBreakMode="tailTruncation" '
                 + (f'numberOfLines="{a["lines"]}" ' if a.get('lines', 1) != 1 else '')
                 + f'baselineAdjustment="alignBaselines" adjustsFontSizeToFit="NO" translatesAutoresizingMaskIntoConstraints="NO" id="{n.id}"{cls_attrs(a)}')
        parts = [f'<label {attrs}>', rect(n), cons_block(n), font(*a['font']), color('textColor', a['color']), '<nil key="highlightedColor"/>', runtime(a), '</label>']
    elif k == 'button':
        attrs = (f'opaque="NO" contentMode="scaleToFill" contentHorizontalAlignment="center" contentVerticalAlignment="center" buttonType="custom" '
                 f'lineBreakMode="middleTruncation" translatesAutoresizingMaskIntoConstraints="NO"' + (f' tag="{a["tag"]}"' if 'tag' in a else '') + f' id="{n.id}"{cls_attrs(a)}')
        title = a.get('title')
        state = (f'<state key="normal" title="{esc(title)}">\n' + color('titleColor', a['tcolor']) + '\n</state>') if title else '<state key="normal"/>'
        acc = f'<accessibility key="accessibilityConfiguration" label="{esc(a["label"])}"/>' if a.get('label') else ''
        parts = [f'<button {attrs}>', rect(n), cons_block(n), acc, font(*a.get('font', (17, 400))), state, bg, runtime(a), connections(n, CUR), '</button>']
    elif k == 'view':
        attrs = f'contentMode="scaleToFill" ' + ('clipsSubviews="YES" ' if a.get('clips') else '') + f'translatesAutoresizingMaskIntoConstraints="NO" id="{n.id}"{cls_attrs(a)}'
        parts = [f'<view {attrs}>', rect(n), kids_block(n), bg, cons_block(n), runtime(a), '</view>']
    elif k == 'image':
        attrs = f'clipsSubviews="YES" userInteractionEnabled="NO" contentMode="scaleAspectFit" horizontalHuggingPriority="251" verticalHuggingPriority="251" image="{a["image"]}" translatesAutoresizingMaskIntoConstraints="NO" id="{n.id}"'
        parts = [f'<imageView {attrs}>', rect(n), cons_block(n), '</imageView>']
    elif k == 'stack':
        attrs = f'opaque="NO" contentMode="scaleToFill" axis="{a.get("axis", "horizontal")}"' + (f' distribution="{a["dist"]}"' if a.get('dist') else '') + (f' alignment="{a["align"]}"' if a.get('align') else '') + (f' spacing="{a["spacing"]}"' if a.get('spacing') else '') + f' translatesAutoresizingMaskIntoConstraints="NO" id="{n.id}"'
        parts = [f'<stackView {attrs}>', rect(n), kids_block(n), cons_block(n), '</stackView>']
    elif k == 'scroll':
        g = n.guides
        attrs = f'clipsSubviews="YES" multipleTouchEnabled="YES" contentMode="scaleToFill" showsHorizontalScrollIndicator="NO" translatesAutoresizingMaskIntoConstraints="NO" id="{n.id}"'
        parts = [f'<scrollView {attrs}>', rect(n), kids_block(n), cons_block(n)] + [f'<viewLayoutGuide key="{x.key}" id="{x.id}"/>' for x in g] + ['</scrollView>']
    elif k == 'textfield':
        attrs = (f'opaque="NO" contentMode="scaleToFill" contentHorizontalAlignment="left" contentVerticalAlignment="center" text="{esc(a["text"])}" '
                 f'placeholder="{esc(a["placeholder"])}" textAlignment="natural" minimumFontSize="17" translatesAutoresizingMaskIntoConstraints="NO" id="{n.id}"{cls_attrs(a)}')
        parts = [f'<textField {attrs}>', rect(n), cons_block(n), color('textColor', 0xFFFFFF), font(17), '<textInputTraits key="textInputTraits" returnKeyType="done" enablesReturnKeyAutomatically="NO"/>', '</textField>']
    else:
        raise ValueError(k)
    return '\n'.join(p for p in parts if p)

def render_scene(sc, device_w=390, device_h=844, canvas=(0, 0)):
    global CUR
    CUR = dict(vc=sc.id)
    sc.finalize()
    root = sc.root
    cls = f' customClass="{sc.vc_class}" customModule="HabitTracker" customModuleProvider="target"' if sc.vc_class else ''
    conns = []
    for prop, node in sc.outlets:
        conns.append(f'<outlet property="{prop}" destination="{node.id}" id="{new_id()}"/>')
    for prop, nodes in sc.collections:
        for nd in nodes:
            conns.append(f'<outletCollection property="{prop}" destination="{nd.id}" collectionClass="NSMutableArray" id="{new_id()}"/>')
    for dest, ident, kind in getattr(sc, 'segues', []):
        extra = ' modalPresentationStyle="fullScreen" modalTransitionStyle="crossDissolve"' if kind == 'presentation' else ''
        conns.append(f'<segue destination="{dest}" kind="{kind}" identifier="{ident}"{extra} id="{new_id()}"/>')
    safe = root.guides[0]
    body = [f'<viewController id="{sc.id}"{cls} sceneMemberID="viewController">',
            f'<view key="view" contentMode="scaleToFill" id="{root.id}">',
            rect(root), '<autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>',
            kids_block(root), f'<viewLayoutGuide key="safeArea" id="{safe.id}"/>',
            color('backgroundColor', root.a['bg']), cons_block(root), '</view>']
    if conns: body.append('<connections>\n' + '\n'.join(conns) + '\n</connections>')
    body.append('</viewController>')
    return '\n'.join(body)

def scene_wrap(inner, cx, cy, sid):
    return (f'<scene sceneID="{sid}">\n<objects>\n{inner}\n'
            f'<placeholder placeholderIdentifier="IBFirstResponder" id="{new_id()}" userLabel="First Responder" customClass="UIResponder" sceneMemberID="firstResponder"/>\n'
            f'</objects>\n<point key="canvasLocation" x="{cx}" y="{cy}"/>\n</scene>')

def document(scenes_xml, initial, resources='', launch=False):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="21701" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" '
            + ('launchScreen="YES" ' if launch else '') +
            f'useTraitCollections="YES" useSafeAreas="YES" colorMatched="YES" initialViewController="{initial}">\n'
            '<device id="retina6_12" orientation="portrait" appearance="dark"/>\n'
            '<dependencies>\n<deployment identifier="iOS"/>\n<plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="21679"/>\n'
            '<capability name="Safe area layout guides" minToolsVersion="9.0"/>\n<capability name="documents saved in the Xcode 8 format" minToolsVersion="8.0"/>\n</dependencies>\n'
            f'<scenes>\n{scenes_xml}\n</scenes>\n{resources}\n</document>\n')
