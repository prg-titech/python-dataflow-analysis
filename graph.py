import type_origin as ty
import random 


class Node:
  def __init__(self, outgoing, typ = ty.Untype()): 
    self.outgoing = outgoing
    self.typ = typ

  def connect(self, node):
    self.outgoing.append(Edge(node))
  
  def __str__(self):
    o = '->'
    for i in range(len(self.outgoing)):
      o = o + f'{self.outgoing[i].dest.name}'
    return o + f'{id(self)}'

  def recieve_type(self, incoming_type):
    # self.typ = self.typ.create_union_type(incoming_type)
    self.typ = ty.Union(self.typ, incoming_type).normalization()

  def send_type(self):
    for i in range(len(self.outgoing)):
      self.outgoing[i].dest.recieve_type(self.typ)
      
      
  def get_outgoing(self):
    lst = []
    for i in range(len(self.outgoing)):
      lst.append(self.outgoing[i].dest)
    return lst


class Source(Node):
  def __init__(self, val, typ):
    self.val = val
    super().__init__(outgoing = [], typ=typ) #Sourceの型でtypを初期化

  def __str__(self):
      return f'{self.val} {super().__str__()}'


class Vertex(Node):
  def __init__(self, name):
    self.name = name
    super().__init__(outgoing = []) #こうしないとインスタンス間でNodeクラスの初期リストが共有される

  def __str__(self):
      return f'{self.name} {super().__str__()}'


class Box(Node):
  def __init__(self, name, num_args):
    self.name = name
    self.args = []
    for i in range(num_args):
      self.args.append(Vertex(f'{i}th Argument Vertex of {name}'))
    self.ret = Vertex(f'return Vertex of {name}')

  def get_arg(self, n):
    return self.args[n]

  def connect_arg(self, n, node):
    self.args[n].connect(node)

  def __str__(self):
    o = ''
    for i in range(len(self.args)):
      o = '' + f'{self.args[i]}'
    return f'{self.name} {super().__str__()}'

  def recieve_type_arg(self, incoming_type, n):
    self.args[n].recieve_type(incoming_type)
    
class Reciever(Vertex):
  def __init__(self, name, method):
    super().__init__(name)
    self.method = method

class MBox(Box):
  def __init__(self, name, num_args):
    super().__init__(name, num_args)
    self.reciever = Reciever(f'Reciever of {name}', self)
    
  def __str__(self):
    return f'メソッド{self.name}'

  def get_reciever(self):
    return self.reciever
  
  def identify_class(self, classes):
    target_classes = []
    
    def sub_identify(name, target_class):
      """ある名前のクラスがtarget_classとのそsuperクラスにあるか特定し、target_classesに加える"""
      if (target_class.name == name):
        target_classes.append(target_class)
      elif (target_class.super_class != None):
        sub_identify(name, target_class.super_class)
    
    #全ての候補となるクラスをtargetclassesに加える
    if not(isinstance(self.reciever.typ, ty.Union)) and isinstance(self.reciever.typ, ty.NewType):
      for target_class in classes:
        sub_identify(self.reciever.typ.name, target_class)
      
    elif (isinstance(self.reciever.typ, ty.Union)):
      # TODO: レシーバの型がUnionのとき
      ...
    
    self.identify_method(target_classes)
  
  def identify_method(self, target_classes):
    """target_classesのそれぞれのクラス内でメソッドがあるか探し、あればメソッド定義側と呼び出し側のレシーバと引数を繋ぐ"""
    
    def exist_method(target_class):
      for method in target_class.method_list:
        if (method.name == self.name):
          print(f'{self}を{target_class}で発見')
          return True, method
      return False, None
    
    def connect_reciever_and_args(method):
      self.reciever.connect(method.reciever) #メソッド定義側と呼び出し側のレシーバを繋ぐ
      for i in range(len(self.args)):
        self.connect_arg(i, method.param_list[i]) #メソッド定義側と呼び出し側の引数を繋ぐ
      print(f'{self}からグラフを再生成しました')
      
    for target_class in target_classes:  
      result, found_method = exist_method(target_class)
      
      if result: #自身で見つかった場合
        connect_reciever_and_args(found_method)
        for child_class in target_class.child_classes:
          result_child , found_method_child = exist_method(child_class)
          if result_child:
            connect_reciever_and_args(found_method_child)
      
      else: #自身で見つからなかった場合
        result_parent, found_method_parent = exist_method(target_class.super_class)
        
        if result_parent:#自身で見つからなかったが、親で見つかった場合
          connect_reciever_and_args(found_method_parent)
          for child_class in target_class.child_classes:
            result_child , found_method_child = exist_method(child_class)
            if result_child:
              connect_reciever_and_args(found_method_child)
              
        else: #自身と親両方で見つからなかった場合
          result_child = False
          for child_class in target_class.child_classes:
            result_child , found_method_child = exist_method(child_class)
            if result_child: break
          if result_child: #自身と親両方で見つからなかったが、子クラスで見つかった場合
            print('found method in sub class')
            ...
          else: #ターゲットクラスとその親子クラスでは見つからなかった場合
            print(f'Not found method {self.name} in {target_class} and related Class')
      
          

class Edge:
  def  __init__(self, dest, typ = 'untyped'):
    self.dest = dest
    # self.typ = typ

  def __str__(self):
      return f' {self.dest}'
    

class Graph:
  def __init__(self):
    self.node_list = []
    self.work_list = []

  def flow(self):
    self.get_source_list0()
    
    while (self.work_list != []):
      target_node = self.work_list[0]
      t = target_node.get_outgoing()
      typlist = []
      for i in range(len(t)):                               
        typlist.append(t[i].typ)
      target_node.send_type()
      self.work_list.pop(0)
      for i in range(len(typlist)):
        if (typlist[i] != t[i].typ):
          self.work_list.append(t[i])
    
    return self
        
  #グラフに含まれるピュアなSourceをリストとして取得
  def get_source_list0(self):
    for i in range(len(self.node_list)):    
      if (isinstance(self.node_list[i], Source)):
        self.work_list.append(self.node_list[i])
        
  def get_source_list(self):
    source_list = []
    for i in range(len(self.node_list)):    
      if (isinstance(self.node_list[i], Source)):
        source_list.append(self.node_list[i])
    return source_list
    
    
class FunctionDef:
  def __init__(self, name, param_list):
    self.body = Graph()
    self.name = name
    self.param_list = [] 
    for i in range(len(param_list)):
      r = random.randint(1, 10)
      self.param_list.append(Vertex('FunctionDef Aragument Vertex: ' + param_list[i]))
    self.ret = Vertex(f'return Vertex of {name}')
    
  def get_source_list(self):
    source_list = []
    for i in range(len(self.body.node_list)):    
      if (isinstance(self.body.node_list[i], Source)):
        source_list.append(self.body.node_list[i])
    return source_list
  
  def connect_arg(self, n, node):
    self.param_list[n].connect(node)
  
    
class MethodDef(FunctionDef):
  def __init__(self, name, reciever, param_list):
    super().__init__(name=name, param_list=param_list )
    self.reciever = RecieverDef(f"{reciever}: Reciever of {name}'s Definition")
    
class RecieverDef(Vertex):
  def __init__(self, name):
    super().__init__(name)
    
  
class Module:
  def __init__(self, name): #関数もGrobalクラスのメソッドとして扱った方が良い？
    self.name = name
    self.body = Graph()  
    self.function_list = []
    self.class_list = []
    self.work_list = []
    
  def __str__(self):
    return f'モジュール{self.name}'
    
  def flow(self, trace):
    self.work_list = self.get_source_list()
    
    while (self.work_list != []):
      # print(f'test{self.work_list}') #デバッグ用
      target_node = self.work_list[0]
      t = target_node.get_outgoing()
      typlist = []
      for i in range(len(t)):
        typlist.append(t[i].typ)
      target_node.send_type()
      self.work_list.pop(0)
      for i in range(len(typlist)):
        if (typlist[i] != t[i].typ):
          self.work_list.append(t[i])
          if (isinstance(t[i], Reciever)): 
            #もしレシーバの型が更新されたら更新された型に基づいてクラスを特定し、メソッドへエッジを引く
            t[i].method.identify_class(self.class_list) 
            self.work_list.extend(t[i].method.args) # 引数を全てワークリストに加える
            
      for i in range(len(self.work_list)):
              print(self.work_list[i], self.work_list[i].typ) #デバッグ用
      if (len(trace) > 0):
        print('tracing:',trace[0].dest, trace[0].dest.typ)
      print('--------------------------') 
            
    return self
    
  def get_source_list(self):
    source_list = []
    source_list.extend(self.body.get_source_list())
    for i in range(len(self.function_list)):
      source_list.extend(self.function_list[i].get_source_list())
    for i in range(len(self.class_list)):
      source_list.extend(self.class_list[i].get_source_list())
    return source_list
    
    
class ClassDef(Module):
  def __init__(self, name, method_list, super_class):
    super().__init__(name=name)
    self.method_list = method_list
    self.super_class = super_class
    if(super_class != None):
      self.super_class.child_classes.append(self)
    self.child_classes = []
    
  def __str__(self):
    return f'クラス{self.name}'
    
  def get_source_list(self):
    source_list = []
    for i in range(len(self.method_list)):
      source_list.extend(self.method_list[i].get_source_list())
    return source_list
    
