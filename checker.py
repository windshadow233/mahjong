from typing import List, Iterable
from copy import deepcopy, copy
from collections import Counter

CHARACTERS = {0, 1, 2, 3, 4, 5, 6, 7, 8}
DOTS = {9, 10, 11, 12, 13, 14, 15, 16, 17}
BAMBOOS = {18, 19, 20, 21, 22, 23, 24, 25, 26}
TERMINALS = {0, 8, 9, 17, 18, 26}
HONORS = {27, 28, 29, 30, 31, 32, 33}
WINDS = {27, 28, 29, 30}
DRAGONS = {31, 32, 33}
TERMINALS_HONORS = {0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33}
GREENS = {19, 20, 21, 23, 25, 32}

ID2NAME = {
    **{i: f"{i + 1}萬" for i in range(9)},
    **{i: f"{i - 8}饼" for i in range(9, 18)},
    **{i: f"{i - 17}索" for i in range(18, 27)},
    27: '東', 28: '南', 29: '西', 30: '北',
    31: '白', 32: '發', 33: '中'
}


class Mahjong:

    def _str2id(self, tiles: str):
        stack = ''
        m = p = s = z = ''
        for c in tiles:
            if c.isdigit():
                stack += c
            elif c == 'm':
                m += stack
                stack = ''
            elif c == 'p':
                p += stack
                stack = ''
            elif c == 's':
                s += stack
                stack = ''
            elif c == 'z':
                z += stack
                stack = ''
            else:
                raise ValueError('Wrong string!')
        if stack != '':
            raise ValueError('Wrong string!')
        if not (all('1' <= _ <= '9' for _ in m + p + s) and all('1' <= _ <= '7' for _ in z)):
            raise ValueError('Wrong string!')
        m = list(map(lambda x: int(x) - 1, sorted(m)))
        p = list(map(lambda x: int(x) + 8, sorted(p)))
        s = list(map(lambda x: int(x) + 17, sorted(s)))
        z = list(map(lambda x: int(x) + 26, sorted(z)))
        return m + p + s + z

    def str2id(self, tiles: str):
        """
        万子:1-9m
        筒子:1-9p
        索子:1-9s
        东南西北:1-4z
        白发中:5-7z
        """
        hand_tiles, *called_tiles = tiles.split(' ')
        hand_tiles = self._str2id(hand_tiles)
        for i, called in enumerate(called_tiles):
            called_tiles[i] = self._str2id(called)
        return hand_tiles, called_tiles

    def _id2str(self, ids: Iterable[int]):
        m = p = s = z = ''
        for id_ in ids:
            if 0 <= id_ < 9:
                m += str(id_ + 1)
            elif 9 <= id_ < 18:
                p += str(id_ - 8)
            elif 18 <= id_ < 27:
                s += str(id_ - 17)
            elif 27 <= id_ < 34:
                z += str(id_ - 26)
            else:
                raise ValueError(f'Wrong ID: {id_}!')
        res = ''
        if m:
            res += ''.join(sorted(m)) + 'm'
        if p:
            res += ''.join(sorted(p)) + 'p'
        if s:
            res += ''.join(sorted(s)) + 's'
        if z:
            res += ''.join(sorted(z)) + 'z'
        return res

    def id2str(self, hand_tiles: Iterable[int], called_tiles: List[List[int]] = None):
        if called_tiles is None:
            called_tiles = []
        hand_tiles = self._id2str(hand_tiles)
        called_tiles = ' '.join(self._id2str(_) for _ in called_tiles)
        return ' '.join([hand_tiles, called_tiles]).strip()

    def _search_triplet(self, tiles: List[int]):
        res = []
        counter = Counter(tiles)
        for c, number in counter.items():
            if number >= 3:
                res.append((c, c, c))
        return res

    def _search_seq(self, tiles: List[int]):
        res = []
        tiles = list(set(tiles))
        tiles.sort()
        for i in range(len(tiles) - 2):
            if tiles[i] in [7, 8, 16, 17, 25, 26, 27, 28, 29, 30, 31, 32, 33]:
                continue
            if tiles[i] + 2 == tiles[i + 1] + 1 == tiles[i + 2]:
                res.append((tiles[i], tiles[i + 1], tiles[i + 2]))
        return res

    def _search_meld(self, tiles: List[int]):
        return self._search_triplet(tiles) + self._search_seq(tiles)

    def is_kong(self, tiles: List[int]):
        return 5 >= len(tiles) >= 4 and len(set(tiles)) == 1

    def is_exposed_kong(self, tiles: List[int]):
        return len(tiles) == 4 and len(set(tiles)) == 1

    def is_concealed_kong(self, tiles: List[int]):
        return len(tiles) == 5 and len(set(tiles)) == 1

    def is_pair(self, tiles: List[int]):
        return len(tiles) == 2 and tiles[0] == tiles[1]

    def is_triplet(self, tiles: List[int]):
        return len(tiles) == 3 and tiles[0] == tiles[1] == tiles[2]

    def is_seq(self, tiles: List[int]):
        return len(tiles) == 3 and tiles[0] + 2 == tiles[1] + 1 == tiles[2] \
               and tiles[0] not in [7, 8, 16, 17, 25, 26, 27, 28, 29, 30, 31, 32, 33]

    def _remove_items(self, tiles: List[int], items: Iterable[int]):
        tiles = copy(tiles)
        for item in items:
            tiles.remove(item)
        return tiles

    def check_called_tiles(self, called_tiles: List[List[int]]):
        for called_meld in called_tiles:
            if not self.is_triplet(called_meld) and not self.is_seq(called_meld) and not self.is_kong(called_meld):
                return False
        return True

    def search_combinations(self, tiles: List[int]):
        res = []
        counter = Counter(tiles)
        if all(i == 2 for i in counter.values()) and len(counter) == 7:
            res.append([(i, i) for i in counter.keys()])

        def split(tiles: List[int], current=None):
            current = current or []
            if len(tiles) == 2 and tiles[0] == tiles[1]:
                current.append((tiles[0], tiles[0]))
                if len(current) > 5:
                    return
                res.append(current)
                return
            melds = self._search_meld(tiles)
            if not melds:
                return
            for meld in melds:
                current.append(meld)
                tiles_left = self._remove_items(tiles, meld)
                split(tiles_left, deepcopy(current))
                current.pop()
        split(tiles)
        res = set([tuple(sorted(_, key=lambda x: (-len(x), x[0]))) for _ in res])
        return res

    def calculate_ready_hand(self, tiles: str, to_str=True):
        """
        听牌计算（必须包含雀头或单骑听雀头的情形）
        万子:1-9m
        筒子:1-9p
        索子:1-9s
        东南西北:1-4z
        白发中:5-7z
        :param tiles: 手牌字符串，若有副露则以空格隔离，例：19m19p19s1234567z，1233m 5555m 789m 123m
        :param to_str: 是否将结果转化为易读的字符串
        """
        hand_tiles, called_tiles = self.str2id(tiles)
        if not self.check_called_tiles(called_tiles):
            return
        if not hand_tiles:
            return
        res = set()
        total_counter = Counter(hand_tiles + sum(called_tiles, []))

        if len(tiles) == 13:
            """Check thirteen orphans"""
            diff = TERMINALS_HONORS.difference(set(hand_tiles))
            diff.update(set(hand_tiles).difference(TERMINALS_HONORS))
            if len(diff) <= 1:
                if len(diff) == 1:
                    res.add(diff.pop())
                else:
                    res.update(TERMINALS_HONORS)
                return self.id2str(res) if to_str else res

        for i in range(34):
            if total_counter[i] < 4:
                r = self.search_combinations(hand_tiles + [i])
                if r:
                    res.add(i)
        return self.id2str(res) if to_str else res