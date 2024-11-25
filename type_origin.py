class Type:
  def __init__(self):
    pass
  
  def __str__(self):
    return f'{self.val}'
  
  def __eq__(self, right):
    return type(self) == type(right)
  
  def subtype_of(self, right):
    return (type(self) == type(right)) or ((type(right) is Union) and (self.subtype_of(right.left) or self.subtype_of(right.right)))
    
  def create_union_type(self, right):
    return right.complete_replace(self)
  
  def normalization(self):
    return self
  
    
    
  #左辺のUnionの要素が右辺のUnionの要素に含まれるかを調べてsubtypeがあるなら左辺の要素に変更supertypeがあるなら何もしない、というのを左辺のUnionの要素の数だけ繰り返す
  
  # def create_union_type(self, right, ret): #retはNone
  #   if(self.subtype_of(right)):
  #     ret = Union(right, ret)
  #   elif(right.subtype_of(self)):
  #     ret = Union(self, ret)
  #   elif (type(right) != Union):
  #     ret = Union(Union(self, right), ret)
  #   else:
  #     self.create_union_type(right.left, ret)
    
    

class Untype(Type):
  def __init__(self):
    pass
  
  def __str__(self):
    return 'Untype'
  
  def subtype_of(self, right):
    return True

class String(Type):
  def __init__(self):
    pass
  def __str__(self):
    return 'String'
  
  def subtype_of(self, right):
    return (type(right) ==  String) or super().subtype_of(right)
  

class Number(Type):
  def __init__(self):
    pass
  
  def __str__(self):
    return 'Number'
  
  def subtype_of(self, right):
    return (type(right) ==  Number) or super().subtype_of(right)

class Int(Number):
  def __init__(self):
    pass
  
  def __str__(self):
    return 'Int'
  
  def subtype_of(self, right):
    return isinstance(right, Int) or super().subtype_of(right)
  
  def create_union_type(self, right):
    return right
  
  
class Boolean(Type):
  def __init__(self):
    pass

  def __str__(self):
    return 'Boolean'
  
  def subtype_of(self, right):
    return isinstance(right, Boolean) or super().subtype_of(right)

class Union(Type): 
  def __init__(self, left, right):
    self.left = left
    self.right = right
    
  def __str__(self):
    return f'Union({self.left.__str__()}, {self.right.__str__()})'
  
  def __eq__(self, right):
    return type(right) == Union and ((self.left.__eq__(right.left) and self.right.__eq__(right.right)) or (self.left.__eq__(right.right) and self.right.__eq__(right.left)))
  
  def subtype_of(self, right):
    return self.left.subtype_of(right) and self.right.subtype_of(right)
  
  def replace_type(self, replacement):
    replaced = False
    
    if isinstance(self.left, Union):
      left, replaced = self.left.replace_type(replacement)
    else:
      if self.left.subtype_of(replacement):
        left = replacement
        replaced = True
      elif (replacement.subtype_of(self.left)):
        left = self.left
        replaced = True
      else:
        left = self.left

    if isinstance(self.right, Union):
      right = self.right.replace_type(replacement)
    else:
      if self.right.subtype_of(replacement):
        right = replacement
        replaced = True
      elif (replacement.subtype_of(self.right)):
        right = self.right
        replaced = True
      else:
        right = self.right

      return (Union(left, right), replaced)
    
  def complete_replace(self, replacement):
    ret, replaced = self.replace_type(replacement)
    if not replaced:
      return Union(self, replacement)
    else: return self
  
  def create_union_type(self, right):
    a = self.left.create_union_type(right)
    b = self.right.create_union_type(a)
    return b
  
  def normalization(self):
    if isinstance(self.left, (Int, Number, String, Boolean, Untype, Function)):
      if (self.left.subtype_of(self.right)):
        return self.right.normalization()
      elif (self.right.subtype_of(self.left)):
        return self.right
      else: return Union(self.left, self.right.normalization())
    else: 
      nleft = self.left.normalization()
      # if isinstance(nleft, Union):
      return Union(nleft.left, Union(nleft.right, self.right)).normalization()
  
  # def get_element_list(self, element_list):
  #   def is_subtype_in_list(element, lst):
  #     return any(element.subtype_of(el) for el in lst)
    
  #   if (type(self.left) != Union):
  #     if not(is_subtype_in_list(self.left, element_list)):
  #       element_list.append(self.left)
  #   else : 
  #     self.left.get_element_list(element_list)
      
  #   if (type(self.right) != Union):
  #     if not(is_subtype_in_list(self.right, element_list)):
  #       element_list.append(self.right)
  #   else : 
  #     self.right.get_element_list(element_list)

  #   return element_list
      
      
  # def create_union_type(self, right):
    
  #   def merge_unique_types(list1, list2):
  #     merged_list = list1[:]  # list1をコピーして新しいリストに
  #     for element in list2:
  #         # list1の型とlist2の型が重複しない場合のみ追加
  #         if not(any(element.subtype_of(el) for el in merged_list)) and :
  #             merged_list.append(element)
  #     return merged_list
  
  #   l = self.get_element_list([])
  #   r = right.get_element_list([])
    
  #   return right
      
    
class Function(Type):
    def __init__(self, param_type, return_type):
        self.param_type = param_type
        self.return_type = return_type

    def __str__(self):
        return f"{self.param_type.__str__()} -> {self.return_type.__str__()}"
      
    def subtype_of(self, right):
      return isinstance(right, Function) and (right.param_type.subtype_of(self.param_type) and self.return_type.subtype_of(right.return_type))
    

class NewType(Type):
  def __init__(self, name):
    self.name = name
    self.super_type_list = []
    super().__init__()    
    
  def __str__(self):
    return f'{self.name}'
    
  def subtype_of(self, right):
    return isinstance(right, NewType) and (right.name in self.super_type_list)


def test_subtype_of(left, right, is_subtype):
  if (left.subtype_of(right) and is_subtype):
    print('This case passed test:', left, 'is subtype of', right)
  elif (not(left.subtype_of(right)) and not(is_subtype)):
    print('This case passed test:', left, 'is not subtype of', right)
  else: 
    print('This case did not pass test')
    
def test_normalization(before, after):
  if (before.normalization() == after): 
    print('This case passed test:', before, 'was normalized to', after)
  else: 
    print('This case did not pass test:', before, 'was not normalized correctly')

# test_subtype_of(Number(), Int(), False)
# test_subtype_of(Int(), Number(), True)
# test_subtype_of(Number(), Union(Number(), String()), True)
# test_subtype_of(String(), Union(Number(), String()), True)
# test_subtype_of(Int(), Union(Union(Number(), String()), String()), True)
# test_subtype_of(Union(Int(), String()), Int(), False)
# test_subtype_of(Union(Int(), String()), Union(Union(Int(), Number()), String()), True)
# test_subtype_of(Function(Number(), Boolean()), Function(Int(), Boolean()), True)
# test_subtype_of(Union(Int(), String()), Union(Number(), String()), True)

  
# test_normalization(String(), String())
# test_normalization(Union(String(), Union(String(), Int())), Union(String(), Int()))
# test_normalization(Union(String(), String()), String())
# test_normalization(Union(Union(String(), Int()), Union(Number(), Boolean())), Union(String(), Union(Number(), Boolean())))
# test_normalization(Union(Function(String(), Int()), String()), Union(Function(String(), Int()), String()))
# test_normalization(Union(Function(String(), Int()), Function(String(), Number())), Function(String(), Number()))
