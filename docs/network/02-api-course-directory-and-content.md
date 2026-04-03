# DGUT Ulearning 课程目录与章节内容接口说明

## 1. 文档范围

本文档说明课程初始化阶段与内容装配阶段的接口，包括课程信息、班级信息、课程目录和章节页面详情接口。

## 2. 课程基础信息接口

### 2.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 课程基础信息 |
| 方法 | `GET` |
| URL | `/uaapi/course/<courseId>/basicinformation` |
| 示例 | `/uaapi/course/55892/basicinformation` |
| 域名 | `https://ua.dgut.edu.cn` |
| 认证要求 | `AUTHORIZATION`、`UA-AUTHORIZATION` |

### 2.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `courseId` | Integer | 是 | 课程 ID |

### 2.3 主要返回字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `course.courseid` | Integer | 课程 ID |
| `course.name` | String | 课程名称 |
| `course.orgid` | Integer | 机构 ID |
| `course.coursetype` | Integer | 课程类型 |
| `publishStatus` | Integer | 发布状态 |

### 2.4 作用说明

| 作用 | 说明 |
| --- | --- |
| 课程名称展示 | 页面标题与课程信息展示 |
| 课程状态校验 | 判断课程是否可正常学习 |
| 课程元信息获取 | 提供后续目录装配的基础上下文 |

## 3. 班级配置接口

### 3.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 班级配置 |
| 方法 | `GET` |
| URL | `/uaapi/classes/<courseId>?classId=<classId>` |
| 示例 | `/uaapi/classes/55892?classId=944483` |
| 域名 | `https://ua.dgut.edu.cn` |

### 3.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `courseId` | Integer | 是 | 课程 ID |
| Query | `classId` | Integer | 是 | 班级 ID |

### 3.3 样例返回字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `classid` | Integer | 班级 ID |
| `takeAgain` | Integer | 是否允许重做 |
| `showCorrect` | Integer | 是否显示正确答案 |

## 4. 课程目录接口

### 4.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 课程目录 |
| 方法 | `GET` |
| URL | `/uaapi/course/stu/<courseId>/directory?classId=<classId>` |
| 示例 | `/uaapi/course/stu/55892/directory?classId=944483` |
| 域名 | `https://ua.dgut.edu.cn` |

### 4.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `courseId` | Integer | 是 | 课程 ID |
| Query | `classId` | Integer | 是 | 班级 ID |

### 4.3 目录返回结构

| 层级 | 字段 | 含义 |
| --- | --- | --- |
| 课程层 | `coursename` | 课程名称 |
| 章节层 | `chapters[].nodetitle` | 章节标题 |
| 章节层 | `chapters[].id` | 目录层章节 ID，对应 `chapterIdForClass` |
| 章节层 | `chapters[].nodeid` | 内部章节节点 ID，对应 `chapterNodeId` |
| 小节层 | `chapters[].items[].itemid` | 小节记录 ID |
| 小节层 | `chapters[].items[].id` | 小节目录 ID |
| 小节层 | `chapters[].items[].title` | 小节标题 |
| 页面层 | `chapters[].items[].coursepages[].id` | 页面对象 ID |
| 页面层 | `chapters[].items[].coursepages[].relationid` | 页面记录关联 ID |
| 页面层 | `chapters[].items[].coursepages[].contentType` | 页面内容类型 |

### 4.4 页面内容类型说明

| `contentType` | 含义 | 备注 |
| --- | --- | --- |
| `6` | 视频页面 | 常见页面标题为“教学视频” |
| `7` | 测试页面 | 章节测验 |

### 4.5 作用说明

| 作用 | 说明 |
| --- | --- |
| 装配课程目录 | 构造 `Course -> Chapter -> Section -> Page` 树 |
| 页面初始定位 | 根据 `chapterId/sectionId/pageId` 确定进入位置 |
| 章节 ID 转换 | 将 URL 层 `chapterId` 转换为内部 `chapterNodeId` |

## 5. 章节页面详情接口

### 5.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 章节页面详情 |
| 方法 | `GET` |
| URL | `/uaapi/wholepage/chapter/stu/<chapterNodeId>` |
| 示例 | `/uaapi/wholepage/chapter/stu/2581780` |
| 域名 | `https://ua.dgut.edu.cn` |

### 5.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `chapterNodeId` | Integer | 是 | 内部章节节点 ID |

### 5.3 返回结构

| 层级 | 字段 | 含义 |
| --- | --- | --- |
| 章节层 | `chapterid` | 章节内部节点 ID |
| 小节层 | `wholepageItemDTOList[].itemid` | 小节记录 ID |
| 页面层 | `wholepageDTOList[].id` | 页面对象 ID |
| 页面层 | `wholepageDTOList[].relationid` | 页面记录关联 ID |
| 页面层 | `wholepageDTOList[].contentType` | 页面内容类型 |
| 页面层 | `wholepageDTOList[].content` | 页面标题或内容名 |
| 组件层 | `coursepageDTOList[].type` | 组件类型 |
| 组件层 | `coursepageDTOList[].resourceid` | 视频或资源业务 ID |
| 组件层 | `coursepageDTOList[].resourceFullurl` | 资源完整地址 |
| 组件层 | `coursepageDTOList[].videoLength` | 视频时长，单位秒 |
| 题目层 | `questionDTOList[].questionid` | 测试页单题 ID |
| 题目层 | `coursepageDTOList[].parentid` | 测试页所属页面对象 ID |

### 5.4 常见组件类型

| `type` | 含义 | 备注 |
| --- | --- | --- |
| `4` | 视频组件 | 页面内实际视频资源 |
| `6` | 试题组件 | 测试页题目对象 |

### 5.5 作用说明

| 作用 | 说明 |
| --- | --- |
| 获取视频清单 | 能直接恢复视频 `videoId`、视频地址、时长 |
| 获取试题内容 | 能恢复测试页题目结构 |
| 页面级内容装配 | 前端据此渲染视频页、测试页等页面 |

### 5.5 测试页补充说明

| 观察项 | 结果 |
| --- | --- |
| 测试页 `contentType` | `7` |
| 试题组件 `type` | `6` |
| 单题 ID 来源 | `questionDTOList[].questionid` |
| 单题答案接口参数 `parentId` | 使用测试页页面对象 ID，即 `wholepageDTOList[].id` |

## 6. 章节与目录接口配合关系

| 阶段 | 接口 | 作用 |
| --- | --- | --- |
| 目录装配阶段 | `/uaapi/course/stu/<courseId>/directory?classId=<classId>` | 提供章节、小节、页面树结构 |
| 章节内容加载阶段 | `/uaapi/wholepage/chapter/stu/<chapterNodeId>` | 提供当前章节的页面详情与视频资源 |

## 7. 当前课程实例验证结论

基于课程 `55892` 的实时请求结果，可以确认：

| 项目 | 结果 |
| --- | --- |
| 课程名称 | `（混合公选）机器的征途：空天科技` |
| 章节数量 | `12` |
| 视频总数量 | `34` |
| 视频总时长 | `22571` 秒，约 `6.27` 小时 |
