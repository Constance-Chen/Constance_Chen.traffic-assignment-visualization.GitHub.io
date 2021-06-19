# ### 2.流量图

# In[182]:


import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from shapely.geometry import LineString,Point
import pyproj
from shapely.ops import transform

path = r"C:..."
UE = r"UE_results_maxIter_new&add.csv"

# 读取文件
vc = pd.read_csv(
    os.path.join(path, UE),usecols=[0,1,7],encoding="unicode_escape"
)

# 预处理
#vc = vc.drop([76])

# 正常读入矢量数据后一定要先变换投影为web墨卡托即EPSG:3857
cd = gpd.read_file('SiouxFallsCoordinates.geojson').to_crs('EPSG:3857')

# 连接表
vc_df = pd.merge(vc, cd, left_on = 'init_node', right_on = 'id').drop(['id'], axis = 1).rename(columns={'x':'init_node_x', 'y':'init_node_y', 'geometry':'init_node_geometry'})

vc_dff = pd.merge(vc_df, cd, left_on = 'term_node', right_on = 'id').drop(['id'], axis = 1).rename(columns={'x':'term_node_x', 'y':'term_node_y', 'geometry':'term_node_geometry'}).reset_index()
vc_dff.head()

def point_line(df):

    # 重组表
    init = pd.DataFrame(df, columns = ['index', 'init_node', 'term_node','V/C' ,'init_node_x', 'init_node_y', 'init_node_geometry'])    .rename(columns={'init_node_x':'x', 'init_node_y':'y',  'init_node_geometry': 'geometry'})
    term = pd.DataFrame(df, columns = ['index', 'init_node', 'term_node','V/C' ,'term_node_x', 'term_node_y', 'term_node_geometry'])    .rename(columns={'term_node_x':'x', 'term_node_y':'y',  'term_node_geometry': 'geometry'})
    data= init.append(term)

    # 根据index分组
    dataGroup = data.groupby('index')

    attrs = [] # 属性信息
    geomList = [] # geometry
    for name, group in dataGroup:
        attrs.append(group.iloc[0,:4]) # 分离出属性信息，取每组的第1行前5列作为数据属性
        xyList = [xy for xy in zip(group.x, group.y)] # 把同一组的点打包到一个list中
        line = LineString(xyList)
        project = pyproj.Transformer.from_proj(pyproj.Proj(init='epsg:4326'),pyproj.Proj(init='epsg:3857')) # wgs84变换投影为web墨卡托即EPSG:3857
        line_new = transform(project.transform, line)  # 投影变换
        geomList.append(line_new)

    # 点转线
    geoDataFrame = gpd.GeoDataFrame(attrs, geometry = geomList)
    return geoDataFrame

vc_gpd = gpd.GeoDataFrame(point_line(vc_dff))
vc_gpd



# 画图

fig, ax = plt.subplots(figsize=(10, 10))

# 构建图层1-8，伪造图例
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='k',linewidth=2.5,label='> 1.75')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='darkred',linewidth=2.5,label='1.50 ~ 1.75')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='crimson',linewidth=2.5,label='1.25 ~ 1.50')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='orangered',linewidth=2.5,label='1.00 ~ 1.25')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='gold',linewidth=2.5,label='0.75 ~ 1.00')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='olive',linewidth=2.5,label='0.50 ~ 0.75')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='olivedrab',linewidth=2.5,label='0.25 ~ 0.50')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='lime',linewidth=2.5,label='< 0.25')

# 为不同v/c设置不同颜色
col=[]
for i in vc_gpd.index:
    if vc_gpd.loc[i, "V/C"]>1.75:
        col.append('k')
    elif vc_gpd.loc[i, "V/C"]>1.5 and vc_gpd.loc[i, "V/C"]<=1.75:
        col.append('darkred')
    elif vc_gpd.loc[i, "V/C"]>1.25 and vc_gpd.loc[i, "V/C"]<=1.5:
        col.append('crimson')
    elif vc_gpd.loc[i, "V/C"]>1.0 and vc_gpd.loc[i, "V/C"]<=1.25:
        col.append('orangered')
    elif vc_gpd.loc[i, "V/C"]>0.75 and vc_gpd.loc[i, "V/C"]<=1.0:
        col.append('gold')
    elif vc_gpd.loc[i, "V/C"]>0.5 and vc_gpd.loc[i, "V/C"]<=0.75:
        col.append('olive')
    elif vc_gpd.loc[i, "V/C"]>0.25 and vc_gpd.loc[i, "V/C"]<=0.5:
        col.append('olivedrab')
    elif vc_gpd.loc[i, "V/C"]>0.0 and vc_gpd.loc[i, "V/C"]<=0.25:
        col.append('lime')

# 图层9 nodes
ax = cd.plot(ax=ax,  edgecolor='k')

# 图层10 links
ax = vc_gpd.plot(ax=ax, color=col, linewidth=2.5)

# 给点添加label
for i in range(cd.shape[0]):
    ax.text(cd.geometry.x[i]+2, cd.geometry.y[i]+2,cd.iat[i,0])

# 单独提前设置图例标题大小
plt.rcParams['legend.title_fontsize'] = 14

# 设置图例标题，位置，排列方式，是否带有阴影
ax.legend(title="V/C Ratio", loc='lower right', ncol=1, shadow=True,bbox_to_anchor=(1.2,0.0),borderaxespad = 0.)

ax.axis('off') # 不显示坐标轴

# 叠加在线地图
#ctx.add_basemap(ax,
#                source='https://a.tile.thunderforest.com/mobile-atlas/{z}/{x}/{y}.png?apikey=41f4f936f1d148f69cbd100812875c88',
#                zoom=15)

fig.savefig('图2.交通流量分配图.png', pad_inches=0, bbox_inches='tight', dpi=1500)

