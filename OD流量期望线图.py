
# coding: utf-8

# ### 1.OD期望线

# In[191]:


import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from shapely.geometry import LineString,Point
import pyproj
from shapely.ops import transform

path = r"C:\...\"
UE = r"demand.dat"

# 读取.dat文件
vc = pd.read_csv(
    os.path.join(path, UE),delimiter="\t",encoding="unicode_escape"
)

#vc

# 正常读入矢量数据后一定要先变换投影为web墨卡托即EPSG:3857
cd = gpd.read_file('SiouxFallsCoordinates.geojson').to_crs('EPSG:3857')

# 连接表
'''
# 相同名的col还是会命名成两列，所以和每次merge重命名一样
origin = pd.merge(vc, cd, left_on = 'origin', right_on = 'id').drop(['id'], axis = 1)
vc_index = pd.merge(origin, cd, left_on = 'dest', right_on = 'id').drop(['id'], axis = 1).reset_index()
vc_df = vc_index.append(vc_index) 
'''
vc_df = pd.merge(vc, cd, left_on = 'origin', right_on = 'id').drop(['id'], axis = 1).rename(columns={'x':'origin_x', 'y':'origin_y', 'geometry':'origin_geometry'})

vc_dff = pd.merge(vc_df, cd, left_on = 'dest', right_on = 'id').drop(['id'], axis = 1).rename(columns={'x':'dest_x', 'y':'dest_y', 'geometry':'dest_geometry'}).reset_index()
vc_dff.head()

def point_line(df):

    # 重组表
    init = pd.DataFrame(df, columns = ['index', 'origin', 'dest','demand' ,'origin_x', 'origin_y', 'origin_geometry'])    .rename(columns={'origin_x':'x', 'origin_y':'y',  'origin_geometry': 'geometry'})
    term = pd.DataFrame(df, columns = ['index', 'origin', 'dest','demand' ,'dest_x', 'dest_y', 'dest_geometry'])    .rename(columns={'dest_x':'x', 'dest_y':'y',  'dest_geometry': 'geometry'})
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
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='peru',linewidth=2.5,label='> 2000')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='yellowgreen',linewidth=2.5,label='1000 ~ 2000')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='yellow',linewidth=2.5,label='500 ~ 1000')
ax = vc_gpd.geometry.plot(ax=ax,edgecolor='ivory',linewidth=2.5,label='< 500')


# 为不同demand设置不同颜色
col=[]
for i in vc_gpd.index:
    if vc_gpd.loc[i, "demand"]>2000:
        col.append('peru')
    elif vc_gpd.loc[i, "demand"]>1000 and vc_gpd.loc[i, "demand"]<=2000:
        col.append('yellowgreen')
    elif vc_gpd.loc[i, "demand"]>500 and vc_gpd.loc[i, "demand"]<=1000:
        col.append('yellow')
    elif vc_gpd.loc[i, "demand"]<=500:
        col.append('ivory')

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
ax.legend(title="Demand", loc='lower right', ncol=1, shadow=True,bbox_to_anchor=(1.2,0.0),borderaxespad = 0.)

ax.axis('off') # 不显示坐标轴

# 叠加在线地图
#ctx.add_basemap(ax,
#                source='https://a.tile.thunderforest.com/mobile-atlas/{z}/{x}/{y}.png?apikey=41f4f936f1d148f69cbd100812875c88',
#                zoom=15)

fig.savefig('图1.OD流量期望线图.png', pad_inches=0, bbox_inches='tight', dpi=1500)
