"""Generate the editable G3 architecture/ETL overview and GitHub SVG preview."""
from html import escape
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

ROOT=Path(__file__).resolve().parents[2]
svg=Element('svg',xmlns='http://www.w3.org/2000/svg',width='1280',height='660',viewBox='0 0 1280 660')
SubElement(svg,'rect',width='1280',height='660',fill='#f5f7fb')
defs=SubElement(svg,'defs')
marker=SubElement(defs,'marker',id='arrow',viewBox='0 0 10 10',refX='9',refY='5',markerWidth='7',markerHeight='7',orient='auto-start-reverse')
SubElement(marker,'path',d='M 0 0 L 10 5 L 0 10 z',fill='#3564a0')
draw=Element('mxfile',host='app.diagrams.net')
page=SubElement(draw,'diagram',name='G3 full pipeline',id='g3')
model=SubElement(page,'mxGraphModel',page='1',pageWidth='1280',pageHeight='660')
tree=SubElement(model,'root')
SubElement(tree,'mxCell',id='0'); SubElement(tree,'mxCell',id='1',parent='0')

def text(x,y,value,size=18,bold=False):
    el=SubElement(svg,'text',x=str(x),y=str(y),fill='#172a43',**{'font-family':'Arial, sans-serif','font-size':str(size),'font-weight':'700' if bold else '400'})
    el.text=value

text(40,58,'Pipeline G3 đủ bốn kỳ và kiểm chạy lại tháng 05',30,True)
text(40,94,'TV3 trên macOS · Python 3.12 · PostgreSQL 18 · G2 dependency còn mở',19)

def box(key,x,y,title,lines):
    SubElement(svg,'rect',x=str(x),y=str(y),width='270',height='170',rx='10',fill='white',stroke='#c5d2e2',**{'stroke-width':'2'})
    text(x+16,y+32,title,21,True)
    for i,line in enumerate(lines): text(x+16,y+67+i*27,line,17)
    cell=SubElement(tree,'mxCell',id=key,parent='1',vertex='1',value=escape(title)+'<br><br>'+'<br>'.join(map(escape,lines)),style='rounded=1;whiteSpace=wrap;html=1;align=left;spacing=15;fontSize=17;fillColor=#ffffff;strokeColor=#c5d2e2;')
    SubElement(cell,'mxGeometry',x=str(x),y=str(y),width='270',height='170',**{'as':'geometry'})

def edge(key,source,target,x1,y1,x2,y2,dashed=False):
    SubElement(svg,'path',d=f'M{x1} {y1} L{x2} {y2}',fill='none',stroke='#3564a0',**{'stroke-width':'2','marker-end':'url(#arrow)',**({'stroke-dasharray':'7 5'} if dashed else {})})
    cell=SubElement(tree,'mxCell',id=key,parent='1',edge='1',source=source,target=target,style='endArrow=block;strokeColor=#3564a0;dashed='+str(int(dashed))+';')
    SubElement(cell,'mxGeometry',relative='1',**{'as':'geometry'})

box('raw',40,145,'12 Parquet TV2',['202503–202506','SHA-256 + schema/bytes','Raw ngoài Git','Inventory + manifest'])
box('source',350,145,'J00 → J01 → J02',['Batch/COPY theo file','Staging → ODS + DQ','file_id + ordinal','FAIL rollback; audit còn'])
box('model',660,145,'J03 → J04 → J05',['3 Dim + 3 Fact','count_value = 1','2 Mart tháng/cơ quan','Upsert key; UNION ALL'])
box('check',970,145,'J06 + quality check',['Source → KPI từng kỳ','Raw–ODS + time roles','PK/FK + Unknown','DAX vẫn PENDING'])
box('handoff',40,390,'TV4 / TV5 nhận review',['TV4 Windows/PBIX','TV4 duyệt catalog/grain','TV5 replay độc lập','G3 chờ TV1 chốt'])
box('reports',350,390,'reports/week3 hoặc QA',['12-file counts + audit','Before/after + exceptions','Catalog quan sát + SQL','Run manifest + code hash'])
box('rerun',660,390,'Chạy lại May thật',['J00–J06 đủ 3 family','Digest có thứ tự PK','So toàn bộ Dim/Fact/Mart','03/04/06 phải giữ nguyên'])
box('transfer',970,390,'Bản DB chuyển riêng',['3 Dim + 2 Mart đủ kỳ','Dump + SHA-256 đã kiểm','Restore kiểm đếm/KPI','Repo: handoff/TV3_G3'])
for i,(a,b) in enumerate([('raw','source'),('source','model'),('model','check')]):
    edge('flow'+str(i),a,b,310+310*i,230,350+310*i,230)
edge('loop','rerun','model',795,390,795,315)
edge('outputs','check','transfer',1105,315,1105,390)
edge('report','rerun','reports',660,475,620,475)
edge('review','reports','handoff',350,475,310,475,True)
text(40,615,'Thiết kế nâng thêm chiều/category chờ TV4. Sơ đồ vật lý G2 vẫn khớp DDL, không đổi grain/FK.',18)
for root,name in [(svg,'10_g3_full_pipeline.svg'),(draw,'10_g3_full_pipeline.drawio')]:
    indent(root)
    ElementTree(root).write(ROOT/'diagrams'/name,encoding='utf-8',xml_declaration=True)
