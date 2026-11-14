# -*- coding: utf-8 -*-
"""Generate original editable SVG diagrams with only the Python standard library."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[2];ASSETS=ROOT/'90-assets/diagrams';ASSETS.mkdir(parents=True,exist_ok=True)
INK='#163047';BLUE='#2667A5';GREEN='#28766B';BG='#F6F8FB';BORDER='#DCE4ED'
def wrap(text,width):
 lines=[];line='';count=0
 for ch in text:
  size=.55 if ord(ch)<128 else 1
  if count+size>width and line:lines.append(line);line='';count=0
  line+=ch;count+=size
 if line:lines.append(line)
 return lines
def rect(es,x,y,w,h,fill,stroke=BORDER,radius=20):es.append(dict(type='rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,radius=radius))
def text(es,x,y,value,size=30,color=INK,bold=False,width=None):
 for i,line in enumerate(wrap(value,width) if width else [value]):es.append(dict(type='text',x=x,y=y+i*int(size*1.5),value=line,size=size,color=color,bold=bold))
def arrow(es,x1,y1,x2,y2):es.append(dict(type='line',x1=x1,y1=y1,x2=x2,y2=y2,color=BLUE));direction=1 if x2>=x1 else -1;es.append(dict(type='polygon',points=[[x2,y2],[x2-direction*13,y2-8],[x2-direction*13,y2+8]],fill=BLUE))
def header(es,kicker,title,subtitle,height=1120):
 rect(es,0,0,1800,height,BG,BG,0);text(es,70,35,kicker,25,BLUE,True);text(es,70,90,title,50,INK,True);text(es,70,170,subtitle,29,INK,width=55)
def card(es,x,y,w,h,label,body,fill='#FFFFFF',size=29):
 rect(es,x,y,w,h,fill);text(es,x+26,y+25,label,30,BLUE,True,width=max(10,int((w-52)/31)));text(es,x+26,y+88,body,size,INK,width=max(10,int((w-52)/size)))
figures=[]
D=json.loads((ROOT/'00-rules/directory-map.json').read_text(encoding='utf-8'))['directories']
for d in D:
 es=[];header(es,d['path'],d['title'],d['purpose'])
 for x,label,body,fill in [(70,'接收什么',d['input'],'#FFFFFF'),(650,'本目录保存',d['stores'],'#EAF2FA'),(1230,'交给哪里',d['output'],'#EAF5F0')]:card(es,x,270,500,350,label,body,fill)
 arrow(es,580,445,638,445);arrow(es,1160,445,1218,445)
 card(es,70,680,810,210,'不要混放',d['avoid'],'#FFFFFF',27);card(es,920,680,810,210,'关键约束',d['rule'],'#FFF6E7',27)
 rect(es,70,930,1660,135,'#FFFFFF');text(es,95,948,'正确使用示例',24,GREEN,True);text(es,95,991,d['example'],25,INK,width=61)
 figures.append(dict(name=d['diagram'],width=1800,height=1120,elements=es))
# Global architecture: original management directories plus explicit engineering regions.
es=[];header(es,'WORKSPACE MAP','一套目录，连接判断、实现与证据','原十个管理目录保留；工程源文件、生成结果与运行数据分开。',1420)
items=[('00-rules','共同规则与执行门槛'),('01-inputs','原始材料与来源'),('02-product','稳定产品事实'),('03-planning','跨需求分析与取舍'),('04-requirement-pool','唯一当前需求状态'),('05-requirements','独立需求与验收定义'),('06-versions','版本、产物、部署与保管'),('07-reviews','真实评审、失败与验证'),('10-code','持续编辑的工程源'),('90-assets','共享资产与说明图'),('99-archive','历史与恢复保管'),('outputs','生成与交付结果'),('.github','明确的仓库检查；不默认生产发布')]
for i,(label,body) in enumerate(items):card(es,60+(i%4)*425,270+(i//4)*255,405,225,label,body,'#EAF2FA' if i<8 else '#EAF5F0',27)
text(es,510,1110,'根Git保管已提交的管理文档和工程',28,INK,True,width=38);text(es,510,1165,'用户数据、凭据及大型私有payload独立受控保管',27,INK,width=38);text(es,60,1335,'读图顺序：规则 → 输入与判断 → 需求 → 版本 → 实施 → 验证 → 反馈',28,GREEN,True)
figures.append(dict(name='overview',width=1800,height=1420,elements=es))
es=[];header(es,'PRODUCT WORKFLOW','从一个输入，走到可核对的交付','每一步有输入、产物和门槛；有代码不等于已批准或已发布。',1220)
steps=[('01 登记来源','01-inputs：保存原意与权限'),('02 理解与规划','02 / 03：核对事实、分析方案'),('03 候选与定义','04 / 05：需求ID、范围和验收'),('04 评审与承诺','07 / 06：人确认取舍和版本'),('05 实施与测试','10-code：提交实现与真实检查'),('06 封存与产物','06 / outputs：精确提交、hash与保管'),('07 授权交付','部署、安装或导出；实际核对'),('08 反馈与复盘','07 → 01：失败保留、新问题再登记')]
positions=[(60+i*425,280) for i in range(4)]+[(60+(3-i)*425,655) for i in range(4)]
for i,((label,body),(x,y)) in enumerate(zip(steps,positions)):card(es,x,y,405,260,label,body,'#EAF2FA' if i<4 else '#EAF5F0',28)
for i in [0,1,2,4,5,6]:
 x,y=positions[i];nx,ny=positions[i+1];arrow(es,x+410 if nx>x else x-5,y+135,nx-6 if nx>x else nx+411,ny+135)
text(es,1340,568,'向下进入实施',25,BLUE,True);es.append(dict(type='line',x1=1535,y1=545,x2=1535,y2=640,color=BLUE))
rect(es,60,990,1680,135,'#FFF6E7');text(es,90,1010,'阶段门槛',26,BLUE,True);text(es,90,1055,'正式批准、生产发布、未授权费用或有损数据操作需要明确依据；AI不能替负责人签字。',27,INK,width=60)
figures.append(dict(name='workflow',width=1800,height=1220,elements=es))
es=[];header(es,'VERSION & RECOVERY','先保管B版，再从A版继续C版','失败迭代也有价值；恢复必须指向精确提交并先独立验证。')
row=[('A：明确基线','记录提交与已知验收'),('B：本次迭代','小步提交；核对未提交内容'),('保管B','归档引用、bundle、hash与收据'),('独立恢复A','验证依赖、构建、测试与兼容'),('C：新路线','保留B；以后可比较或复用提交')]
for i,(label,body) in enumerate(row):card(es,60+i*340,300,320,330,label,body,'#EAF2FA' if i<3 else '#EAF5F0',27)
for i in range(4):arrow(es,384+i*340,465,396+i*340,465)
for i,(label,body) in enumerate([('源码取回','Git历史和文档可恢复'),('运行包切换','目标环境真实可用'),('数据兼容','先保管当前数据，不盲降级')]):card(es,60+i*570,730,540,230,label,body,'#FFF6E7',27)
text(es,60,1030,'三个恢复结论分别验证；本机bundle不等于异地备份，也不等于应用已恢复运行。',26,GREEN,True,width=63)
figures.append(dict(name='versioning',width=1800,height=1120,elements=es))
es=[];header(es,'SOURCE / ARTIFACT / RECORD / DATA','源文件、结果、登记、运行数据各司其职','完整工作空间可以被理解与复刻，不需要把秘密和所有大文件都提交。',1140)
for x,y,label,body,fill in [(60,280,'10-code：源文件','持续编辑的实现、测试、提示词、可编辑工程与运行资源。','#EAF2FA'),(930,280,'outputs：结果','构建包、导出、评测与恢复探测；通常忽略本体。','#EAF5F0'),(60,665,'06 / 07：可核对记录','精确提交、产物ID/hash、当前目标和实际验证；不伪造成功。','#FFFFFF'),(930,665,'独立受控：运行数据','数据库、媒体、账户、秘密与签名私钥；不进入普通Git。','#FFF6E7')]:card(es,x,y,810,300,label,body,fill,30)
text(es,60,1050,'发布：封存 → 不可变产物 → 目标环境验证 → 具体授权 → 实际核对 → 更新登记',27,GREEN,True,width=64)
figures.append(dict(name='publishing',width=1800,height=1140,elements=es))
es=[];header(es,'AI BOOTSTRAP','把模板交给AI，在空目录建立真实项目','先完整阅读，再检查目标；只初始化结构，不编造产品与上线事实。')
for i,(label,body) in enumerate([('01 读完整文档','README、AGENTS、规则和目录图'),('02 核对目标','位置、已有文件、权限和本轮范围'),('03 Dry-run','显示将复制什么，不写文件'),('04 生成并验证','只接受空目标，保留空表与空组件')]):card(es,60+i*425,300,405,315,label,body,'#EAF2FA' if i<3 else '#EAF5F0',28)
for i in range(3):arrow(es,470+i*425,455,479+i*425,455)
card(es,60,720,810,245,'目标非空：停止覆盖','只读盘点，保管现有状态，另定迁移方案；不能删掉旧文件来绕过拒绝。','#FFF6E7',28);card(es,930,720,810,245,'目标为空：诚实起步','名称来自用户；需求、组件、部署与封存登记没有真实动作就保持空白。','#FFFFFF',28)
text(es,60,1030,'初始化不创建云资源、业务应用或远端仓库；阶段批准和生产动作需要明确授权。',26,GREEN,True,width=64)
figures.append(dict(name='ai-bootstrap',width=1800,height=1120,elements=es))
for f in figures:
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{f["width"]}" height="{f["height"]}" viewBox="0 0 {f["width"]} {f["height"]}" role="img">',f'<title>{html.escape(f["name"])}</title>']
 for e in f['elements']:
  if e['type']=='rect':out.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" rx="{e["radius"]}" fill="{e["fill"]}" stroke="{e["stroke"]}"/>')
  elif e['type']=='text':out.append(f'<text x="{e["x"]}" y="{e["y"]+e["size"]}" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="{e["size"]}" font-weight="{700 if e["bold"] else 400}" fill="{e["color"]}">{html.escape(e["value"])}</text>')
  elif e['type']=='line':out.append(f'<line x1="{e["x1"]}" y1="{e["y1"]}" x2="{e["x2"]}" y2="{e["y2"]}" stroke="{e["color"]}" stroke-width="4"/>')
  elif e['type']=='polygon':out.append('<polygon points="'+' '.join(str(x)+','+str(y) for x,y in e['points'])+'" fill="'+e['fill']+'"/>')
 out.append('</svg>');(ASSETS/(f['name']+'.svg')).write_text('\n'.join(out)+'\n',encoding='utf-8')
local=ROOT/'outputs/diagram-layout.json';local.parent.mkdir(parents=True,exist_ok=True);local.write_text(json.dumps(figures,ensure_ascii=False),encoding='utf-8');print('Generated '+str(len(figures))+' SVG diagrams and a local raster layout.')
