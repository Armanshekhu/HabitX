#!/usr/bin/env python3
"""Generates Main.storyboard and LaunchScreen.storyboard from the design's CSS metrics."""
from ib import *

BG, CARD, TILE, ACC = 0x0F0F15, 0x1A1A2E, 0x252540, 0x6C63FF
NAV, T2, T3, GOLD, GREEN, PINK, RED, ICON = 0x8B7BFF, 0xB0B0C0, 0x8A8AA3, 0xF59E0B, 0x34D399, 0xF472B6, 0xF87171, 0xB77BF5
W = 390

# ---------- helpers ----------
def mk_root(sc_cls):
    root = Node('view', (0, 0, 390, 844), bg=BG)
    root.safe = root.guide('safeArea')
    sc = Scene(sc_cls, root)
    return root, sc

def label(text, size, weight, col, frame, cls=None, kern=None, lh=None, lines=1, align='natural'):
    rt = []
    if kern is not None: rt.append(('kern', 'real', kern))
    if lh is not None: rt.append(('lineHeight', 'real', lh))
    return Node('label', frame, text=text, font=(size, weight), color=col, cls=cls or ('HTLabel' if rt else None), rt=rt, lines=lines, align=align)

def card(frame, radius=14, clips=False, bg=CARD):
    return Node('view', frame, bg=bg, clips=clips, rt=[('layer.cornerRadius', 'int', radius)])

def LR(sc, n, l=16, r=16):
    sc.con(n, 'leading', n.parent, 'leading', l)
    sc.con(n, 'trailing', n.parent, 'trailing', -r)
def L(sc, n, c=16): sc.con(n, 'leading', n.parent, 'leading', c)
def R(sc, n, c=16): sc.con(n, 'trailing', n.parent, 'trailing', -c)
def T(sc, n, c): sc.con(n, 'top', n.parent, 'top', c)
def B(sc, n, c): sc.con(n, 'bottom', n.parent, 'bottom', -c)
def below(sc, n, prev, gap): sc.con(n, 'top', prev, 'bottom', gap)
def Wd(sc, n, w, rel=None): sc.con(n, 'width', c=w, rel=rel)
def Ht(sc, n, h): sc.con(n, 'height', c=h)

def nav_row(root, sc, back_title, title, title_dx):
    """Back button (8,56) + centred title. Returns (back, title)."""
    back = Node('button', (8, 56, 72, 44), cls='NavButton', title=back_title, tcolor=NAV, font=(17, 400),
                rt=[('iconName', 'string', 'back')], actions=['backTapped:'], label=None)
    root.add(back)
    sc.con(back, 'leading', root, 'leading', 8)
    sc.con(back, 'top', root.safe, 'top', 9)
    Ht(sc, back, 44); Wd(sc, back, 44, 'greaterThanOrEqual')
    t = label(title, 17, 600, 0xFFFFFF, (160, 68, 80, 20))
    root.add(t)
    sc.con(t, 'centerX', root, 'centerX', title_dx)
    sc.con(t, 'centerY', back, 'centerY')
    return back, t

def scroll_area(root, sc, top_item, content_h):
    scroll = Node('scroll', (0, 100, 390, 744))
    content = Node('view', (0, 0, 390, content_h))
    scroll.add(content); root.add(scroll)
    clg, flg = scroll.guide('contentLayoutGuide'), scroll.guide('frameLayoutGuide')
    sc.con(scroll, 'top', top_item, 'bottom')
    sc.con(scroll, 'leading', root, 'leading'); sc.con(scroll, 'trailing', root, 'trailing'); sc.con(scroll, 'bottom', root, 'bottom')
    sc.con(content, 'top', clg, 'top'); sc.con(content, 'bottom', clg, 'bottom')
    sc.con(content, 'leading', clg, 'leading'); sc.con(content, 'trailing', clg, 'trailing')
    sc.con(content, 'width', flg, 'width')
    return scroll, content

def h1(text, frame):
    return label(text, 34, 700, 0xFFFFFF, frame, kern=0.2)

def cap(text, frame):
    return label(text.upper(), 11, 500, T3, frame, kern=1)

# ---------- Splash ----------
def splash(nav_id=None):
    root, sc = mk_root('SplashViewController')
    logo = Node('image', (143, 300, 104, 104), image='Logo')
    title = label('Habit Tracker', 30, 700, 0xFFFFFF, (115, 428, 160, 36), kern=0.2)
    sub = label('Small steps, every day', 15, 400, T2, (115, 472, 160, 18))
    bar = Node('view', (115, 714, 160, 6), cls='ProgressBarView', rt=[('progress', 'real', 0.6)])
    loading = label('Loading your habits', 13, 400, T3, (115, 732, 160, 16))
    root.add(logo, title, sub, bar, loading)
    sc.con(logo, 'centerX', root, 'centerX'); sc.con(logo, 'top', root, 'top', 300); Wd(sc, logo, 104); Ht(sc, logo, 104)
    sc.con(title, 'centerX', root, 'centerX'); below(sc, title, logo, 24)
    sc.con(sub, 'centerX', root, 'centerX'); below(sc, sub, title, 8)
    sc.con(loading, 'centerX', root, 'centerX'); sc.con(loading, 'bottom', root, 'bottom', -96)
    sc.con(bar, 'centerX', root, 'centerX'); sc.con(bar, 'bottom', loading, 'top', -12)
    Wd(sc, bar, 160); Ht(sc, bar, 6)
    sc.outlets.append(('progressBar', bar))
    return sc

# ---------- Today ----------
def today(stats_id, new_id_):
    root, sc = mk_root('TodayViewController')
    chart = Node('button', (294, 56, 44, 44), cls='NavButton', tcolor=NAV, rt=[('iconName', 'string', 'chart')],
                 label='Statistics', segue=(stats_id, 'showStats'))
    plus = Node('button', (338, 56, 44, 44), cls='NavButton', tcolor=NAV, rt=[('iconName', 'string', 'plus'), ('iconStroke', 'real', 2)],
                label='Add habit', segue=(new_id_, 'showNewHabit'))
    root.add(chart, plus)
    sc.con(plus, 'trailing', root, 'trailing', -8); sc.con(plus, 'top', root.safe, 'top', 9)
    sc.con(chart, 'trailing', plus, 'leading'); sc.con(chart, 'centerY', plus, 'centerY')
    for b in (chart, plus): Ht(sc, b, 44); Wd(sc, b, 44)

    scroll, c = scroll_area(root, sc, plus, 688)
    date = label('Tuesday, November 24', 15, 400, T2, (16, 4, 358, 18))
    title = h1('Today', (16, 22, 358, 41))
    c.add(date, title)
    L(sc, date); T(sc, date, 4); L(sc, title); below(sc, title, date, 0)

    xc = card((16, 79, 358, 109)); c.add(xc)
    LR(sc, xc); below(sc, xc, title, 16)
    lvl = label('Level 3', 12, 400, T3, (16, 14, 60, 14))
    xp = label('240 XP', 28, 800, GOLD, (16, 28, 110, 31))
    streak = label('5 day streak', 14, 600, GOLD, (260, 42, 98, 17))
    bar = Node('view', (16, 69, 326, 6), cls='ProgressBarView', rt=[('progress', 'real', 0.4)])
    nxt = label('60 XP to Level 4', 12, 400, T3, (16, 81, 110, 14))
    xc.add(lvl, xp, streak, bar, nxt)
    L(sc, lvl); T(sc, lvl, 14); L(sc, xp); below(sc, xp, lvl, 0)
    R(sc, streak); sc.con(streak, 'bottom', xp, 'bottom')
    LR(sc, bar); below(sc, bar, xp, 10); Ht(sc, bar, 6)
    L(sc, nxt); below(sc, nxt, bar, 6); B(sc, nxt, 14)

    dl = label('Daily progress', 15, 400, T2, (16, 208, 120, 18))
    dc = label('3 / 5', 15, 600, 0xFFFFFF, (330, 208, 44, 18))
    pb = Node('view', (16, 234, 358, 6), cls='ProgressBarView', rt=[('progress', 'real', 0.6)])
    pl = label('Finish all 5 for a +20 XP perfect day bonus', 12, 400, T3, (16, 246, 300, 14))
    c.add(dl, dc, pb, pl)
    L(sc, dl); below(sc, dl, xc, 20); R(sc, dc); sc.con(dc, 'centerY', dl, 'centerY')
    LR(sc, pb); below(sc, pb, dl, 8); Ht(sc, pb, 6)
    L(sc, pl); below(sc, pl, pb, 6)

    st = Node('stack', (16, 284, 358, 380), axis='vertical', spacing=10); c.add(st)
    LR(sc, st); below(sc, st, pl, 24); B(sc, st, 24)

    sc.outlets += [('dateLabel', date), ('levelLabel', lvl), ('xpLabel', xp), ('streakLabel', streak), ('xpBar', bar),
                   ('toNextLabel', nxt), ('progressCountLabel', dc), ('progressBar', pb), ('perfectLabel', pl), ('habitsStack', st)]
    return sc

# ---------- Statistics ----------
def stats(rewards_id):
    root, sc = mk_root('StatsViewController')
    back, _ = nav_row(root, sc, 'Today', 'Statistics', 3.5)
    scroll, c = scroll_area(root, sc, back, 1100)
    title = h1('Statistics', (16, 4, 358, 41)); c.add(title)
    L(sc, title); T(sc, title, 4)

    row = Node('stack', (16, 61, 358, 73), axis='horizontal', dist='fillEqually', spacing=10); c.add(row)
    LR(sc, row); below(sc, row, title, 16)
    vals = {}
    for i, (name, val, col, out) in enumerate([('This Week', '71%', ICON, 'weekLabel'), ('Best Streak', '21', GREEN, 'bestLabel'), ('Active', '5', PINK, 'activeLabel')]):
        cd = card((i * 122.67, 0, 112.67, 73)); row.add(cd)
        a = label(name, 11, 500, T3, (12, 12, 80, 13)); b = label(val, 28, 800, col, (12, 27, 60, 34))
        cd.add(a, b)
        L(sc, a, 12); T(sc, a, 12); L(sc, b, 12); below(sc, b, a, 2); B(sc, b, 12)
        sc.outlets.append((out, b))

    lc = card((16, 144, 358, 82)); c.add(lc)
    LR(sc, lc); below(sc, lc, row, 10)
    ll = label('Level 3', 15, 600, 0xFFFFFF, (16, 14, 60, 18)); lx = label('240 XP', 15, 700, GOLD, (290, 14, 68, 18))
    lb = Node('view', (16, 42, 326, 6), cls='ProgressBarView', rt=[('progress', 'real', 0.4)])
    ln = label('60 XP to Level 4', 12, 400, T3, (16, 54, 110, 14))
    lc.add(ll, lx, lb, ln)
    L(sc, ll); T(sc, ll, 14); R(sc, lx); T(sc, lx, 14)
    LR(sc, lb); below(sc, lb, ll, 10); Ht(sc, lb, 6)
    L(sc, ln); below(sc, ln, lb, 6); B(sc, ln, 14)
    sc.outlets += [('levelLabel', ll), ('xpLabel', lx), ('xpBar', lb), ('toNextLabel', ln)]

    c1 = cap('Activity', (16, 250, 100, 13)); c.add(c1); L(sc, c1); below(sc, c1, lc, 24)
    hc = card((16, 271, 358, 216)); c.add(hc); LR(sc, hc); below(sc, hc, c1, 8)
    hm = Node('view', (16, 16, 326, 184), cls='HeatmapView'); hc.add(hm)
    LR(sc, hm); T(sc, hm, 16); B(sc, hm, 16); Ht(sc, hm, 184)
    sc.outlets.append(('heatmapView', hm))

    c2 = cap('Streaks', (16, 511, 100, 13)); c.add(c2); L(sc, c2); below(sc, c2, hc, 24)
    sk = card((16, 532, 358, 228), clips=True); c.add(sk); LR(sc, sk); below(sc, sk, c2, 8)
    ss = Node('stack', (0, 0, 358, 228), axis='vertical'); sk.add(ss)
    for e in ('leading', 'trailing', 'top', 'bottom'): sc.con(ss, e, sk, e)
    sc.outlets.append(('streaksStack', ss))

    c3 = cap('Badges', (16, 784, 100, 13)); c.add(c3); L(sc, c3); below(sc, c3, sk, 24)
    bs = Node('stack', (16, 805, 358, 212), axis='vertical', spacing=16); c.add(bs)
    LR(sc, bs); below(sc, bs, c3, 8)
    sc.outlets.append(('badgesStack', bs))

    btn = Node('button', (16, 1033, 358, 44), cls='HTButton', title='How rewards work', tcolor=NAV, font=(17, 400), segue=(rewards_id, 'showRewards'))
    c.add(btn); LR(sc, btn); below(sc, btn, bs, 16); Ht(sc, btn, 44); B(sc, btn, 24)
    return sc

# ---------- New Habit ----------
def new_habit():
    root, sc = mk_root('NewHabitViewController')
    back, _ = nav_row(root, sc, 'Today', 'New Habit', 3.75)
    scroll, c = scroll_area(root, sc, back, 760)

    tile = Node('view', (16, 12, 72, 72), cls='IconTileView'); c.add(tile)
    L(sc, tile); T(sc, tile, 12); Wd(sc, tile, 72); Ht(sc, tile, 72)
    hint = label('Tap to change icon', 15, 400, T2, (104, 38, 150, 18)); c.add(hint)
    sc.con(hint, 'leading', tile, 'trailing', 16); sc.con(hint, 'centerY', tile, 'centerY')

    c1 = cap('Choose icon', (16, 108, 120, 13)); c.add(c1); L(sc, c1); below(sc, c1, tile, 24)
    grid = Node('stack', (16, 129, 358, 284), axis='vertical', spacing=10); c.add(grid)
    LR(sc, grid); below(sc, grid, c1, 8)

    c2 = cap('Name', (16, 437, 100, 13)); c.add(c2); L(sc, c2); below(sc, c2, grid, 24)
    fld = Node('textfield', (16, 458, 358, 48), cls='PaddedTextField', text='Morning Run', placeholder='Habit name'); c.add(fld)
    LR(sc, fld); below(sc, fld, c2, 8); Ht(sc, fld, 48)

    c3 = cap('Repeat on', (16, 530, 120, 13)); c.add(c3); L(sc, c3); below(sc, c3, fld, 24)
    days = Node('stack', (16, 551, 358, 44), axis='horizontal', dist='fillEqually', spacing=6); c.add(days)
    LR(sc, days); below(sc, days, c3, 8); Ht(sc, days, 44)
    btns = []
    for i, (ch, nm) in enumerate(zip('MTWTFSS', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])):
        b = Node('button', (i * 52, 0, 46, 44), cls='HTButton', title=ch, tcolor=ICON, font=(15, 600), tag=i, label=nm, actions=['dayTapped:'])
        days.add(b); btns.append(b)

    xpl = label('Every check-in earns +10 XP', 14, 600, GOLD, (16, 615, 250, 17)); c.add(xpl)
    L(sc, xpl); below(sc, xpl, days, 20)
    save = Node('button', (16, 648, 358, 52), cls='HTButton', title='Save Habit', tcolor=0xFFFFFF, font=(17, 600), bg=ACC,
                rt=[('layer.cornerRadius', 'int', 14)], actions=['saveTapped:'])
    c.add(save); LR(sc, save); below(sc, save, xpl, 16); Ht(sc, save, 52)
    disc = Node('button', (16, 708, 358, 44), cls='HTButton', title='Discard Habit', tcolor=RED, font=(17, 400), actions=['discardTapped:'])
    c.add(disc); LR(sc, disc); below(sc, disc, save, 8); Ht(sc, disc, 44); B(sc, disc, 24)

    sc.outlets += [('scrollView', scroll), ('previewTile', tile), ('iconGrid', grid), ('nameField', fld)]
    sc.collections.append(('dayButtons', btns))
    return sc

# ---------- Rewards ----------
def rewards():
    root, sc = mk_root('RewardsViewController')
    back, _ = nav_row(root, sc, 'Back', 'How rewards work', 1)
    items = [('+10 XP', 'Check in', "Complete a habit for today. Unchecking it takes the XP back, so it can't be farmed.", 105),
             ('+20 XP', 'Perfect day', 'Complete every habit scheduled for today. Awarded once per day.', 86),
             ('100 XP', 'One level', 'Level = total XP \u00f7 100, rounded down, plus 1.', 86),
             ('Streak', 'Scheduled days only', "Days a habit isn't scheduled never break the streak.", 86),
             ('Badges', 'Earned once', 'First Check-in, 3-Day Streak, 7-Day Streak, Perfect Day, 50 Check-ins, Level 5.', 105)]
    total = 61 + sum(i[3] for i in items) + 10 * 4 + 24
    scroll, c = scroll_area(root, sc, back, total)
    t = h1('Rewards', (16, 4, 358, 41)); c.add(t); L(sc, t); T(sc, t, 4)
    prev, y = t, 61
    for k, (a, b, d, h) in enumerate(items):
        cd = card((16, y, 358, h)); c.add(cd); LR(sc, cd); below(sc, cd, prev, 16 if k == 0 else 10)
        xp = label(a, 15, 800, GOLD, (16, 14, 64, 18)); tt = label(b, 15, 600, 0xFFFFFF, (94, 14, 200, 18))
        ds = label(d, 14, 400, T2, (94, 34, 248, h - 48), lh=18.9, lines=0)
        cd.add(xp, tt, ds)
        L(sc, xp); T(sc, xp, 14); Wd(sc, xp, 64)
        sc.con(tt, 'leading', xp, 'trailing', 14); T(sc, tt, 14)
        sc.con(ds, 'leading', tt, 'leading'); R(sc, ds); below(sc, ds, tt, 2); B(sc, ds, 14)
        prev, y = cd, y + h + 10
    sc.con(c.children[-1], 'bottom', c, 'bottom', -24)
    return sc

# ---------- assemble Main.storyboard ----------
sp, td, st, nh, rw = splash(), None, None, None, None
nav_id = new_id()
rw = rewards()
st = stats(rw.id)
nh = new_habit()
td = today(st.id, nh.id)
sp.segues = [(nav_id, 'showMain', 'presentation')]

scenes = []
scenes.append(scene_wrap(render_scene(sp), -900, 0, new_id()))
nav = (f'<navigationController id="{nav_id}" customClass="HTNavigationController" customModule="HabitTracker" customModuleProvider="target" sceneMemberID="viewController">\n'
       f'<navigationBar key="navigationBar" contentMode="scaleToFill" id="{new_id()}">\n<rect key="frame" x="0.0" y="47" width="390" height="44"/>\n<autoresizingMask key="autoresizingMask"/>\n</navigationBar>\n'
       f'<connections>\n<segue destination="{td.id}" kind="relationship" relationship="rootViewController" id="{new_id()}"/>\n</connections>\n</navigationController>')
scenes.append(scene_wrap(nav, -300, 0, new_id()))
for i, s in enumerate([td, st, nh, rw]):
    scenes.append(scene_wrap(render_scene(s), 300 + i * 700, 0, s.sid))
open('../HabitTracker/Main.storyboard', 'w').write(document('\n'.join(scenes), sp.id, '<resources>\n<image name="Logo" width="104" height="104"/>\n</resources>'))

# ---------- LaunchScreen.storyboard (static copy of the splash) ----------
root = Node('view', (0, 0, 390, 844), bg=BG); root.safe = root.guide('safeArea')
ls = Scene(None, root)
logo = Node('image', (143, 300, 104, 104), image='Logo')
title = label('Habit Tracker', 30, 700, 0xFFFFFF, (115, 428, 160, 36)); title.a['cls'] = None
sub = label('Small steps, every day', 15, 400, T2, (115, 472, 160, 18))
bar = Node('view', (115, 714, 160, 6), bg=TILE)
fill = Node('view', (0, 0, 96, 6), bg=ACC); bar.add(fill)
loading = label('Loading your habits', 13, 400, T3, (115, 732, 160, 16))
root.add(logo, title, sub, bar, loading)
ls.con(logo, 'centerX', root, 'centerX'); ls.con(logo, 'top', root, 'top', 300); Wd(ls, logo, 104); Ht(ls, logo, 104)
ls.con(title, 'centerX', root, 'centerX'); below(ls, title, logo, 24)
ls.con(sub, 'centerX', root, 'centerX'); below(ls, sub, title, 8)
ls.con(loading, 'centerX', root, 'centerX'); ls.con(loading, 'bottom', root, 'bottom', -96)
ls.con(bar, 'centerX', root, 'centerX'); ls.con(bar, 'bottom', loading, 'top', -12); Wd(ls, bar, 160); Ht(ls, bar, 6)
ls.con(fill, 'leading', bar, 'leading'); ls.con(fill, 'top', bar, 'top'); ls.con(fill, 'bottom', bar, 'bottom'); Wd(ls, fill, 96)
open('../HabitTracker/LaunchScreen.storyboard', 'w').write(
    document(scene_wrap(render_scene(ls), 0, 0, ls.sid), ls.id, '<resources>\n<image name="Logo" width="104" height="104"/>\n</resources>', launch=True))
print('storyboards written')
