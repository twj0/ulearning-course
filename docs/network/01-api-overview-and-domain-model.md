# DGUT Ulearning 网站 API 总览与领域模型

## 1. 文档目的

本文档用于对 DGUT Ulearning 网站的接口体系进行标准化说明，明确各域名职责、核心资源对象、关键 ID 映射关系及整体调用链路。

## 2. 系统域名分工

| 域名 | 系统层级 | 主要职责 | 典型接口 |
| --- | --- | --- | --- |
| `https://ua.dgut.edu.cn` | 学习业务层 | 课程目录、章节内容、学习记录初始化、学习记录同步、心跳保活 | `/uaapi/course/...`、`/uaapi/wholepage/...`、`/uaapi/studyrecord/...`、`/uaapi/yws/api/personal/sync` |
| `https://lms.dgut.edu.cn` | 平台层 | 课程平台入口、课程行为打点、用户菜单与权限 | `/courseapi/behavior/watchVideo`、`/courseapi/users/menu/userMenuList`、`/courseapi/textbook/student/information` |
| `https://obscloud.ulearning.cn` | 资源层 | 视频封面与 MP4 媒体流分发 | `/resources/web/<media-id>.mp4`、`/resources/web/<media-id>.mp4?vframe/jpg/offset/1` |

## 3. 核心资源对象

| 对象 | 说明 | 主要来源接口 |
| --- | --- | --- |
| `Course` | 课程对象，承载课程级目录和班级上下文 | `/uaapi/course/<courseId>/basicinformation`、`/uaapi/course/stu/<courseId>/directory?classId=<classId>` |
| `Chapter` | 章节对象，包含多个小节 | `/uaapi/course/stu/<courseId>/directory?classId=<classId>` |
| `Section` | 小节对象，承担学习记录初始化和提交 | `/uaapi/course/stu/<courseId>/directory?classId=<classId>`、`/uaapi/studyrecord/...` |
| `Page` | 页面对象，承载视频、试题、口语等组件 | `/uaapi/wholepage/chapter/stu/<chapterNodeId>` |
| `Video` | 页面中的视频组件资源 | `/uaapi/wholepage/chapter/stu/<chapterNodeId>` |
| `Question` | 测试页中的单题对象，承载题干、选项与答案查询入口 | `/uaapi/wholepage/chapter/stu/<chapterNodeId>`、`/uaapi/questionAnswer/<questionid>?parentId=<pageId>` |
| `StudyRecord` | 节、页、视频三层学习记录 | `/uaapi/studyrecord/item/<itemid>?courseType=4`、`/uaapi/yws/api/personal/sync?courseType=4&platform=PC` |

## 4. 入口 URL 模型

课程学习页入口示例：

```text
https://ua.dgut.edu.cn/learnCourse/learnCourse.html?courseId=55892&chapterId=136397207&classId=944483&returnUrl=https%3A%2F%2Flms.dgut.edu.cn%2Fcourseweb%2Fulearning%2Findex.html%23%2Fcourse%2Ftextbook%3FcourseId%3D160508
```

### 4.1 URL 参数说明

| 参数 | 示例值 | 含义 | 备注 |
| --- | --- | --- | --- |
| `courseId` | `55892` | UA 学习页课程 ID | 后续目录、课程详情接口直接使用 |
| `chapterId` | `136397207` | 章节定位 ID | 用于初始定位，不等于后续行为接口中的同名字段 |
| `sectionId` | 未在样例中出现 | 小节定位 ID | 可用于直接进入某小节 |
| `pageId` | 未在样例中出现 | 页面定位 ID | 优先级高于 `sectionId` 和 `chapterId` |
| `classId` | `944483` | 班级 ID | 目录、班级信息、行为上报均依赖该值 |
| `returnUrl` | LMS 页面地址 | 返回上层课程页 | 不参与学习记录计算 |

### 4.2 初始定位优先级

| 优先级 | 定位依据 | 说明 |
| --- | --- | --- |
| 1 | `pageId` | 直接进入指定页面 |
| 2 | `sectionId` | 进入指定小节的第一页 |
| 3 | `chapterId` | 进入指定章节的第一页 |
| 4 | `localStorage` 历史位置 | 恢复上次学习位置 |
| 5 | 课程首个页面 | 默认兜底入口 |

## 5. ID 体系与映射关系

当前网站中存在多层 ID，同名字段并不总处于同一语义层级。该关系是理解接口行为的关键。

| ID 类型 | 样例值 | 所在层级 | 用途 |
| --- | --- | --- | --- |
| `courseId` | `55892` | 课程层 | UA 学习页课程标识 |
| `classId` | `944483` | 班级层 | 班级上下文 |
| URL `chapterId` | `136397207` | 目录层 | 用于页面初始定位，对应 `Chapter.idForClass()` |
| `chapterNodeId` | `2581780` | 内部章节层 | 行为打点、章节详情接口使用，对应 `Chapter.id()` |
| `itemid` | `2584634` | 小节层 | 学习记录初始化、心跳、同步提交使用 |
| `pageid` | `6848124` | 页面层 | 页面业务对象 ID |
| `relationid` | `2584635` | 页面记录层 | 页面学习记录关联 ID |
| `questionid` | `18692023` | 题目层 | 测试页单题 ID |
| `videoId` | `1717243` | 视频业务层 | `watchVideo` 与学习记录视频对象使用 |
| `media-id` | `17405354188653939` | 资源文件层 | 实际 MP4 资源路径使用 |

### 5.1 关键映射说明

| 映射关系 | 说明 |
| --- | --- |
| `Chapter.idForClass()` -> URL `chapterId` | 页面入口参数使用的章节 ID |
| `Chapter.id()` -> `chapterNodeId` | 行为接口和章节详情接口使用的章节内部节点 ID |
| `Page.id()` -> 页面对象 ID | 页面内容装配使用 |
| `Page.relationId()` -> 页面记录关联 ID | 学习记录恢复与同步使用 |
| `Question.id()` -> `questionid` | 单题答案查询使用 |
| `Page.id()` -> `questionAnswer.parentId` | 测试页答案查询使用 |
| `Video.resourceId` -> `videoId` | 学习行为和记录使用 |
| `Video.resourceFullurl` -> MP4 地址 | 媒体播放实际使用 |

### 5.2 `2026-04-03` 实测映射样例

以如下学习页链接为例：

```text
https://ua.dgut.edu.cn/learnCourse/learnCourse.html?courseId=60251&chapterId=136356084&classId=941992&returnUrl=https%3A%2F%2Flms.dgut.edu.cn%2Fcourseweb%2Fulearning%2Findex.html%23%2Fcourse%2Ftextbook%3FcourseId%3D159530
```

实际目录解析结果为：

| 字段 | 实测值 | 说明 |
| --- | --- | --- |
| `courseId` | `60251` | UA 课程 ID |
| URL `chapterId` | `136356084` | 目录层章节 ID |
| `chapterNodeId` | `2602181` | 通过目录接口映射得到的内部章节节点 ID |
| `itemid` | `2773463` | 该章节下目标小节 |
| 测试页数量 | `7` | 该小节下共有 `7` 个 `contentType=7` 页面 |

这再次说明：URL 里的 `chapterId` 只是目录层定位参数，真正用于章节详情、答题解析与学习记录提交的是内部 `chapterNodeId`。

## 6. 认证与请求头模型

### 6.1 Token 来源

| 来源 | 优先级 | 说明 |
| --- | --- | --- |
| Cookie `token` | 1 | 正常学习模式默认使用 |
| URL 参数 `token` | 2 | Cookie 缺失时作为兜底 |

### 6.2 常见认证头

| 请求头 | 说明 |
| --- | --- |
| `AUTHORIZATION` | 主认证头 |
| `UA-AUTHORIZATION` | UA 学习页附加认证头 |
| `Accept-Language` | 语言环境 |
| `Referer` | 页面来源校验 |
| `Origin` | 跨域接口校验，常见于 `watchVideo` |

## 7. 总体调用链路

### 7.1 学习页初始化链路

| 顺序 | 阶段 | 主要动作 | 典型接口 |
| --- | --- | --- | --- |
| 1 | 读取入口参数 | 解析 `courseId/classId/chapterId/...` | 页面本地逻辑 |
| 2 | 读取登录态 | 从 Cookie 读取 `token` | 页面本地逻辑 |
| 3 | 配置全局请求头 | 写入 `AUTHORIZATION/UA-AUTHORIZATION` | 页面本地逻辑 |
| 4 | 读取课程信息 | 获取课程基础信息 | `/uaapi/course/<courseId>/basicinformation` |
| 5 | 读取班级配置 | 获取班级学习设置 | `/uaapi/classes/<courseId>?classId=<classId>` |
| 6 | 读取课程目录 | 生成课程章节树 | `/uaapi/course/stu/<courseId>/directory?classId=<classId>` |
| 7 | 定位目标章节 | 将 URL `chapterId` 映射为内部 `chapterNodeId` | 页面本地逻辑 |
| 8 | 加载章节内容 | 拉取当前章所有页面与组件 | `/uaapi/wholepage/chapter/stu/<chapterNodeId>` |
| 9 | 读取节学习记录 | 恢复 section/page/video 记录 | `/uaapi/studyrecord/item/<itemid>?courseType=4` |
| 10 | 进入当前页 | 启动页面学习与视频播放器 | 页面本地逻辑 |

### 7.2 视频学习链路

| 顺序 | 阶段 | 主要动作 | 典型接口 |
| --- | --- | --- | --- |
| 1 | 请求媒体资源 | 拉取 MP4 数据 | `https://obscloud.ulearning.cn/resources/web/<media-id>.mp4?token=...` |
| 2 | 行为打点 | 标记开始观看某视频 | `/courseapi/behavior/watchVideo` |
| 3 | 本地累积学习状态 | 更新 `viewTime`、`positionTime`、`startEndTimeList` | 页面本地逻辑 |
| 4 | 心跳保活 | 防作弊与会话保活 | `/uaapi/studyrecord/heartbeat/<itemid>/<studyStartTime>` |
| 5 | 自动或手动保存 | 提交 section/page/video 记录 | `/uaapi/yws/api/personal/sync?courseType=4&platform=PC` |

### 7.3 测试页答案链路

| 顺序 | 阶段 | 主要动作 | 典型接口 |
| --- | --- | --- | --- |
| 1 | 加载测试页结构 | 获取测试页题目结构与 `questionid` | `/uaapi/wholepage/chapter/stu/<chapterNodeId>` |
| 2 | 初始化测试会话 | 为测试小节创建学习会话 | `/uaapi/studyrecord/initialize/<itemid>` |
| 3 | 心跳保活 | 维持测试页学习会话 | `/uaapi/studyrecord/heartbeat/<itemid>/<studyStartTime>` |
| 4 | 拉取单题答案 | 按题号读取 `correctAnswerList` | `/uaapi/questionAnswer/<questionid>?parentId=<pageId>` |

## 8. 后续文档索引

| 编号文档 | 内容 |
| --- | --- |
| `02-api-course-directory-and-content.md` | 课程目录与章节内容接口 |
| `03-api-study-record-and-sync.md` | 学习记录、心跳与同步提交接口 |
| `04-api-video-playback-and-behavior.md` | 视频流接口与播放行为接口 |
| `05-api-course-55892-chapter-video-inventory.md` | 课程 `55892` 的章节与视频清单 |
| `12-api-test-page-and-question-answer.md` | 测试页结构与题目答案接口 |
