import graph as graph
import type_origin as ty

##############################################
#例
class A:
    ...
    def foo(self, x):
        return x + 10
        
class B:
    ...
    def foo(self, x):
        return x + 20
    
        
a = A()
a.foo(30)

##############################################

#須田が想像する上記の例の解析の手順

#⓪あるファイル（モジュール）で解析を始める際にモジュールオブジェクトを生成する
test_module = graph.Module('Test') #↑が定義されているモジュール

#①classBを見つけたら新たにClassDefクラスのインスタンスを作り、Moduleのclass_listに追加する
classA = graph.ClassDef('A', [], None)
test_module.class_list.append(classA)

#②中を見ていってメソッドが見つかったら新たにMethodDefクラスのインタンスを作り、ClassDefのmethod_listに追加する
fooA = graph.MethodDef('foo', 'self', ['x'])
classA.method_list.append(fooA)

#③メソッドの中身を見ていき、グラフを作る(ノードを作り、エッジを引く。順番は？)
ten = graph.Source(10, ty.Int())
plus1 = graph.Box('+', 2)
fooA.connect_arg(0, plus1.args[0])
ten.connect(plus1.args[1])
plus1.connect_arg(0, plus1.ret)
plus1.connect_arg(1, plus1.ret)
plus1.ret.connect(fooA.ret)#本当はここで組み込み関数の+のFunctionDefのパラメータVertexにエッジが引かれて返り値VertexからBoxの返り値Vertexにエッジが引かれる

#④メソッド定義の最後まで見終わったら作ったグラフをFunctionDefのnode_list(＝グラフ)に代入して紐づけておく
fooA.body.node_list.extend([ten, plus1])

#クラスBも同様
classB = graph.ClassDef('B', [], None)
test_module.class_list.append(classB)

fooB = graph.MethodDef('foo', 'self', ['x'])
classB.method_list.append(fooB)

xB = graph.Vertex('x')
twenty = graph.Source(20, ty.Int())
plus2 = graph.Box('+', 2)
xB.connect(plus2.args[0])
twenty.connect(plus2.args[1])
plus2.connect_arg(0, plus2.ret)
plus2.connect_arg(1, plus2.ret)
plus2.ret.connect(fooB.ret)

fooB.body.node_list.extend([xB, twenty, plus2])

# print(xB)
# print(plus2.ret)

# ⑤クラス定義を全て見終わったら外にでてきてグラフ生成を再開
a = graph.Vertex('a')
s1 = graph.Source('A()', ty.NewType('A'))
s2 = graph.Source('30', ty.Int())
foo_mbox1 = graph.MBox('foo', 1)

s1.connect(a)
a.connect(foo_mbox1.reciever)
s2.connect(foo_mbox1.args[0])
# print(s1)
# print(a)

#⑥ノードを全て生成し終わったら属するモジュールのbodyに加える
test_module.body.node_list.extend([a, s1, s2, foo_mbox1])

# ⑦グラフを生成し終わったら型を流す
test_module.flow(foo_mbox1.args[0].outgoing)
# print(s1.typ,a.typ,foo_mbox1.reciever.typ) #全てにAが流れていることを確認（typがNewType('A')）
# print(foo_mbox1.args[0].typ)
print(foo_mbox1.args[0], foo_mbox1.args[0].typ)
print(foo_mbox1.reciever, foo_mbox1.reciever.typ)
print(foo_mbox1.reciever.outgoing[0].dest, foo_mbox1.reciever.outgoing[0].dest.typ)

##############################################
#追加でこのような例をかんがえる
class C:
    ...
    def foo(self, x):
        return x + 30

class D(C):
    ...
##############################################
# 解析中（flowが行われている最中）に、レシーバの型が変化したときに呼ばれ、メソッドのクラスを特定し、エッジを繋ぐidentify_classメソッドのテスト

#上のコードに対応するグラフを簡易生成
classC = graph.ClassDef('C', [], None)
fooC = graph.MethodDef('foo', 'self', ['x'])
classC.method_list.append(fooC)
classD = graph.ClassDef('D', [], classC)

#テスト
# foo_mbox1.identify_class([classA, classB]) #Aで見つかる
# foo_mbox1.identify_class([classB]) #Bだけでは見つからない

# foo_mbox2 = graph.MBox('foo', 1)
# foo_mbox2.reciever.typ = ty.NewType('C') #テストのため人工的に代入

# foo_mbox2.identify_class([classD]) #親クラスでfooを発見する
# foo_mbox2.identify_class([classA, classB]) #fooのレシーバの型はCなのでクラスA,Bからは見つからない
# print(foo_mbox2.reciever) #Top LevelとLow Levelがつながっているのがわかる（これはレシーバ）
# print(foo_mbox2.args[0])


#### 


#
#やったこと
#New_Typeなるものを追加した
#FunctionDef,MethodDef,ClassDef,Moduleを追加した
#   解析(flow)はモジュールのメソッドとなり、Moduleが解析中のプログラム全体を表すクラスに変更した
#   色々解析の構造を変えた
#MBox全然手をつけてなかったのでちゃんと実装した
#オブジェクトがそこそこ良い感じに表示されるようにした
#そもそも解析でクラスを扱えるようにした
#メソッドのクラスを特定できるようにした(????)

#わかってないこと
#ある型が流れてるけど実際は違う型のオブジェクトである。というのは具体的にどういう場合？
#   A<:B, a: Bだけどa = a()みたいなこと？
#コードからグラフ生成のやり方
#   組み込みはどうする？
#   簡単な例は作れそうだけど複雑になると時間がかかりそう
#   なんか良いライブラリはある？(ASTではなく有効グラフを生成するような)
#   そもそもTypeProfは直接グラフを生成してるわけではなさそう？（コードは須田には難解）

#できそうだけどやってないこと
#TODO: flow内でグラフ生成と解析を交互に行うアルゴリズムの実装
#TODO: 他の例でテスト
#   循環がある場合(以前動いていたのでこれくらいの変更で動かなくなることはなさそうだが...)
#   ネストされたクラス定義
#   Module内に関数やクラスや通常のプログラムが混在している例
#TODO: もっと早くする（コードの余計な部分をなくす）



def test_identify_class(b, c, d):
    """テスト用"""
    print('----------------------------')
    method = graph.MBox('foo', 0)
    method.reciever.typ = ty.NewType('C')
    if (d == 1):
        classD = graph.ClassDef('D', method_list=[method], super_class=None)
    else:
        classD = graph.ClassDef('D', method_list=[], super_class=None)     
    if (c == 1):
        classC = graph.ClassDef('C', method_list=[method], super_class=classD)
    else:
        classC = graph.ClassDef('C', method_list=[], super_class=classD)    
    if (b == 1):
        classB = graph.ClassDef('B', method_list=[method], super_class=classC)
    else:
        classB = graph.ClassDef('B', method_list=[], super_class=classC)
    classes = [classC]
    method.identify_method(classes)

test_identify_class(0,0,0)
test_identify_class(0,0,1)
test_identify_class(0,1,0)
test_identify_class(0,1,1)
test_identify_class(1,0,0) #このケースだけまだ
test_identify_class(1,0,1)
test_identify_class(1,1,0)
test_identify_class(1,1,1)
