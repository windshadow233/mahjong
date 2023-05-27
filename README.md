# 一个<del>可能存在bug的</del>立直麻将计算器

作为日本立直麻将的新手玩家，在和朋友线下面麻时，计算不清符数、漏掉本该有的番数是常有的事，更是可能会遇到"整牌1分钟，打牌2分钟，结算3分钟"的尴尬场景。 
为了避免此种现象的发生以及提升自己对立直麻将结算规则的熟悉程度，我花了三两天时间，写了一个计算器。

因非大规模使用，脚本并没有采用打表的方法，而是使用普通的深度优先搜索算法来拆分手牌。

同时为了偷懒，使用了一款非常方便的傻瓜式web框架streamlit。

体验地址: [立直麻将计算器](https://mahjong.fyz666.xyz)
