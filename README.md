# Constance-Chen.username.GitHub.io
## 高等网络流分析

Task 1 采用UE分配评估当前交通网络流<br>
Task 2 识别当前网络问题<br>
Task 3 改善当前路网问题

### 数据来源

Network：Sioux Falls network<br>
Data source：https://www.bgu.ac.il/~bargera/tntp/

```markdown
OD需求期望线图
1. 读取.dat文件
2. 读取.geojson文件
- 正常读入矢量数据后一定要先变换投影为web墨卡托即EPSG:3857
3. 连接和重组表
4. point2line
5. 可视化
- 基于contextily叠加在线地图
```
```markdown
交通流量分配图
1. 读取.dat文件
2. 读取.geojson文件
- 正常读入矢量数据后一定要先变换投影为web墨卡托即EPSG:3857
3. 连接和重组表
4. point2line
5. 可视化
- 基于contextily叠加在线地图
```
