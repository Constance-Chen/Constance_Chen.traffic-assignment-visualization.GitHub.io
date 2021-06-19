# Constance-Chen.username.GitHub.io
## 高等网络交通流分析

Task 1 采用UE分配评估当前交通网络流<br>
Task 2 识别当前网络问题<br>
Task 3 改善当前路网问题

## 数据来源

Network：Sioux Falls network<br>
Data source：https://www.bgu.ac.il/~bargera/tntp/

## OD需求期望线图
### 0.配置环境
```python
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from shapely.geometry import LineString,Point
import pyproj
from shapely.ops import transform
```
### 1. 读取.dat文件
```python
od = pd.read_csv(
    os.path.join(path, UE),delimiter="\t",encoding="unicode_escape"
)
```
### 2. 读取.geojson文件
- 正常读入矢量数据后一定要先变换投影为web墨卡托即EPSG:3857
```python
cd = gpd.read_file('SiouxFallsCoordinates.geojson').to_crs('EPSG:3857')
```
### 3. 连接和重组表
```python
od_df = pd.merge(od, cd, left_on = 'origin', right_on = 'id').drop(['id'], axis = 1).rename(columns={'x':'origin_x', 'y':'origin_y', 'geometry':'origin_geometry'})

od_dff = pd.merge(od_df, cd, left_on = 'dest', right_on = 'id').drop(['id'], axis = 1).rename(columns={'x':'dest_x', 'y':'dest_y', 'geometry':'dest_geometry'}).reset_index()
od_dff.head()
```
### 4. point2line
```python
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
```
### 5. 可视化
- 添加nodes, links, labels
```python
fig, ax = plt.subplots(figsize=(10, 10))

# 构建图层1-8，伪造图例
ax = od_gpd.geometry.plot(ax=ax,edgecolor='peru',linewidth=2.5,label='> 2000')
ax = od_gpd.geometry.plot(ax=ax,edgecolor='yellowgreen',linewidth=2.5,label='1000 ~ 2000')
ax = od_gpd.geometry.plot(ax=ax,edgecolor='yellow',linewidth=2.5,label='500 ~ 1000')
ax = od_gpd.geometry.plot(ax=ax,edgecolor='ivory',linewidth=2.5,label='< 500')


# 为不同demand设置不同颜色
col=[]
for i in od_gpd.index:
    if od_gpd.loc[i, "demand"]>2000:
        col.append('peru')
    elif od_gpd.loc[i, "demand"]>1000 and od_gpd.loc[i, "demand"]<=2000:
        col.append('yellowgreen')
    elif od_gpd.loc[i, "demand"]>500 and od_gpd.loc[i, "demand"]<=1000:
        col.append('yellow')
    elif od_gpd.loc[i, "demand"]<=500:
        col.append('ivory')

# 图层9 nodes
ax = cd.plot(ax=ax,  edgecolor='k')

# 图层10 links
ax = od_gpd.plot(ax=ax, color=col, linewidth=2.5)

# 给点添加label
for i in range(cd.shape[0]):
    ax.text(cd.geometry.x[i]+2, cd.geometry.y[i]+2,cd.iat[i,0])

# 单独提前设置图例标题大小
plt.rcParams['legend.title_fontsize'] = 14

# 设置图例标题，位置，排列方式，是否带有阴影
ax.legend(title="Demand", loc='lower right', ncol=1, shadow=True,bbox_to_anchor=(1.2,0.0),borderaxespad = 0.)

ax.axis('off') # 不显示坐标轴
```
- 基于contextily叠加在线地图
```python
# 叠加在线地图
ctx.add_basemap(ax,
                source='https://a.tile.thunderforest.com/mobile-atlas/{z}/{x}/{y}.png?apikey=41f4f936f1d148f69cbd100812875c88',
                zoom=15)
```
交通流量分配图同理。<br>
![Image](https://github.com/Constance-Chen/Constance-Chen.username.GitHub.io/raw/main/pic/图2.交通流量分配图.png)
## Ref.
1. 叠加在线地图
https://github.com/CNFeffery/DataScienceStudyNotes
2. UE算法交通分配traffic assignment
Pramesh Kumar. (2019, October 10). prameshk/Traffic-Assignment: Static Traffic Assignment using User Equilibrium and Stochastic User Equilibrium- Python Code (Version 2.0). Zenodo. http://doi.org/10.5281/zenodo.3479554


