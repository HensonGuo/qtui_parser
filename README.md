### Features

1. 界面与逻辑分离，代码编写更加精简美观，不需要花费太长的时间用代码用调整界面，将更多的精力用来关注逻辑的编写与实现
![](http://cc.fp.ps.netease.com/file/5fb7755c5e60276c1a6abd841icbEsTi02)
2. 充分利用qt设计师的功能，提高生产力
3. 资源加载方式方便快捷，可根据具体需求灵活设置

### vs.Pyuic&Xmlui
1. 目前项目中的xmlui需要手动编辑，缺少可视化工具，效率比较低
2. pyuic生成的py文件可读性差，关联的qrc资源文件需要打包在模板内，增大模板体积

### How2use
UI创建：
```python
widget = UIParser().parse(uiFilePath, loadRes=False, parentWidget=None, debug=False)
```
参数说明：

* uiFilePath：ui文件路径可以根据具体需求设置，abspath/qrcpath/zippath都可，如：
```python
UIParser().parse(r"D:\Work\apps_wonderful\transformer\gamelive\ent_vote\entertainment_vote\ui\fans_club.ui", loadRes=True)
```
```python
UIParser().parse("z/gamelive_right_region/fan_badge/fans_club.ui", loadRes=True)
```
```python
UIParser().parse(":/gamelive/kill_dragon_activity/kill_dragon.ui")
```
使用qrc的路径时，需要将ui文件一起打包，其他方式的资源路径因为资源和模板分离的，需要将loadRes设置true
* loadRes: 是否加载资源，为true会根据uiFilePath所在目录对qrc每个节点的资源文件建立映射，会去替换stylesheet和pixmap中的资源路径
* parentWidget: 给生成的ui指定的父widget
* debug: 为true时会将ui节点的创建及属性设置的流程打印到控制台

查找组件对象：
```python
UIParser().parse("z/gamelive_right_region/fan_badge/fans_club.ui", True, self, False)

UiFinder.findQLabel(self, "myRankValueLabel").setText(rank)

UiFinder.findQPushButton(self,  "btnJoin").clicked.connect(
    GameLiveInterface.instance().jionFunClub
)
```