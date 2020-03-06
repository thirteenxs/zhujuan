# 颜色字典
color_dic={
    '黑色':30,
    '红色':31,
	'绿色':32,
	'黃色':33,
	'蓝色':34,
	'紫红色':35,
	'青蓝色':36,
	'白色':37

}

# 背景色色字典
background_color_dic={
    '黑色':40,
    '红色':41,
	'绿色':42,
	'黃色':43,
	'蓝色':44,
	'紫红色':45,
	'青蓝色':46,
	'白色':47
}
###显示方式字典

type_dic={
'终端默认设置':0,
'高亮显示':1,
'使用下划线':4,
'闪烁':5,
'反白显示':7,
'不可见':8
}

def sprint(type,color,background_color,text):
    l_text='\033[{0};{1};{2}m'.format(type,color,background_color)
    r_text='\033[0m'
    print(l_text+text+r_text,end='')

def sinput(type,color,background_color,text):
    l_text='\033[{0};{1};{2}m'.format(type,color,background_color)
    r_text='\033[0m'
    return input(l_text+text+r_text)

