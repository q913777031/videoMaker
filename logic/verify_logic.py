"""逻辑题制作前核验：用户提供的枚举代码 + 独立的全条件枚举 + 反证分支。不出现在正片中。"""

from itertools import permutations

cities = ('北京', '上海', '广州')
sports = ('篮球', '足球', '排球')

# A. 用户提供的原始校验代码（逐字）
solutions = []
for city in permutations(cities):
    for sport in permutations(sports):
        if city[0] == '广州' or city[1] == '上海' or sport[1] == '排球':
            continue
        if sport[city.index('北京')] != '足球':
            continue
        if sport[city.index('上海')] != '篮球':
            continue
        solutions.append((city, sport))
assert solutions == [(('上海', '北京', '广州'), ('篮球', '足球', '排球'))]
print('校验通过：36种组合中仅有1个解。')

# B. 独立写法：显式列出五条条件，统计组合总数与每条条件的筛除数
people = ('甲', '乙', '丙')
conds = {
    '①甲不来自广州': lambda c, s: c['甲'] != '广州',
    '②乙不来自上海': lambda c, s: c['乙'] != '上海',
    '③北京的人喜欢足球': lambda c, s: all(s[p] == '足球' for p in people if c[p] == '北京'),
    '④上海的人喜欢篮球': lambda c, s: all(s[p] == '篮球' for p in people if c[p] == '上海'),
    '⑤乙不喜欢排球': lambda c, s: s['乙'] != '排球',
}
total, sols = 0, []
for cp in permutations(cities):
    for sp in permutations(sports):
        total += 1
        c, s = dict(zip(people, cp)), dict(zip(people, sp))
        if all(f(c, s) for f in conds.values()):
            sols.append((c, s))
assert total == 36, total
assert len(sols) == 1, sols
c, s = sols[0]
assert c == {'甲': '上海', '乙': '北京', '丙': '广州'} and s == {'甲': '篮球', '乙': '足球', '丙': '排球'}
for name, f in conds.items():
    assert f(c, s)
    print(f'回代 {name}：满足')
print(f'独立枚举：{total} 种组合，{len(sols)} 个解 → ' + '；'.join(f'{p}-{c[p]}-{s[p]}' for p in people))

# C. 反证：假设乙来自广州，检查是否存在满足全部条件的组合
contra = [(cc, ss) for cc, ss in
          ((dict(zip(people, cp)), dict(zip(people, sp))) for cp in permutations(cities) for sp in permutations(sports))
          if cc['乙'] == '广州' and all(f(cc, ss) for f in conds.values())]
assert contra == []
print('反证：乙来自广州时无解，乙只能来自北京。')

# D. 中间推论：③④ + 一一对应 ⇒ 广州的人必喜欢排球（在满足③④的全部组合中成立）
for cp in permutations(cities):
    for sp in permutations(sports):
        cc, ss = dict(zip(people, cp)), dict(zip(people, sp))
        if conds['③北京的人喜欢足球'](cc, ss) and conds['④上海的人喜欢篮球'](cc, ss):
            assert all(ss[p] == '排球' for p in people if cc[p] == '广州')
print('推论核验：满足③④的所有组合中，广州的人都喜欢排球。')
