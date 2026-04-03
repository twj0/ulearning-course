# DGUT Ulearning 会话时序与抓包要求说明

## 1. 文档范围

本文档用于说明当前已观察会话的时序规律，以及在后续分析中需要抓取哪些网络活动才能完成特定层级的还原。

## 2. 已验证时序模型

### 2.1 学习页初始化时序

| 顺序 | 阶段 | 说明 |
| --- | --- | --- |
| 1 | 进入学习页 | 打开 `learnCourse.html` |
| 2 | 课程与班级上下文加载 | 获取课程基础信息、班级配置 |
| 3 | 课程目录加载 | 获取 chapter、section、page 树结构 |
| 4 | 章节内容加载 | 获取当前章节的页面详情与视频资源 |
| 5 | 学习记录恢复 | 读取 section/page/video 的历史记录 |
| 6 | 进入页面学习 | 页面进入学习状态，播放器初始化 |

### 2.2 视频学习时序

| 顺序 | 阶段 | 说明 |
| --- | --- | --- |
| 1 | 请求 MP4 | 浏览器向 `obscloud.ulearning.cn` 请求视频数据 |
| 2 | 行为打点 | 触发 `watchVideo` |
| 3 | 心跳保活 | 约每 `100` 秒一次 |
| 4 | 自动同步 | 约每 `5` 分钟一次 `personal/sync` |
| 5 | 完成后继续保活 | 完成状态形成后 heartbeat 仍继续 |

## 3. 单视频会话样例时间线

以下时间线基于 `2026-04-02 20:49:55` 的会话 HAR。

| 时间 | 事件 | 接口 |
| --- | --- | --- |
| `20:49:25` | 请求 MP4 数据 | `GET /resources/web/17405354188653939.mp4?token=...` |
| `20:49:26` | 视频行为打点 | `POST /courseapi/behavior/watchVideo` |
| `20:50:18` | 第 1 次心跳 | `GET /uaapi/studyrecord/heartbeat/2584634/1775134119` |
| `20:51:58` | 第 2 次心跳 | 同上 |
| `20:53:35` | 第 1 次自动同步 | `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` |
| `20:53:38` | 第 3 次心跳 | 同上 |
| `20:55:18` | 第 4 次心跳 | 同上 |
| `20:56:58` | 第 5 次心跳 | 同上 |
| `20:58:35` | 第 2 次自动同步 | 同上 |
| `20:58:38` | 第 6 次心跳 | 同上 |
| `21:00:18` | 第 7 次心跳 | 同上 |
| `21:01:58` | 第 8 次心跳 | 同上 |
| `21:03:35` | 第 3 次自动同步 | 同上 |
| `21:03:38` | 第 9 次心跳 | 同上 |
| `21:05:18` | 第 10 次心跳 | 同上 |

## 4. 已验证周期规律

| 观察项 | 结果 |
| --- | --- |
| 心跳周期 | 约 `100` 秒 |
| 自动同步周期 | 约 `300` 秒 |
| `watchVideo` 触发时机 | 开始看某视频时 |
| 完成后是否继续同步 | 是 |
| 完成后是否继续 heartbeat | 是 |

## 5. 不同分析目标对应的抓包要求

### 5.1 目标一：恢复整门课的章节与视频清单

| 最少需要的网络活动 | 说明 |
| --- | --- |
| `GET /uaapi/course/stu/<courseId>/directory?classId=<classId>` | 恢复完整目录树 |
| `GET /uaapi/wholepage/chapter/stu/<chapterNodeId>` | 恢复每章页面视频资源 |

### 5.2 目标二：分析某个视频的开始播放与完成同步

| 最少需要的网络活动 | 说明 |
| --- | --- |
| `POST /courseapi/behavior/watchVideo` | 确认播放行为打点 |
| `GET /uaapi/studyrecord/heartbeat/<itemid>/<studyStartTime>` | 确认保活节奏 |
| `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` | 确认完成态与进度同步 |
| `GET /resources/web/<media-id>.mp4?token=...` | 确认实际媒体资源 |

### 5.3 目标三：分析从零开始观看到首次完成

| 最少需要的网络活动 | 说明 |
| --- | --- |
| `GET /uaapi/studyrecord/initialize/<itemid>` | 确认学习会话开始时间 |
| `GET /uaapi/studyrecord/item/<itemid>?courseType=4` | 确认初始历史进度 |
| `POST /courseapi/behavior/watchVideo` | 确认开始观看 |
| MP4 流请求 | 确认视频资源 |
| 至少一条首次 `complete=1` 的 `personal/sync` | 确认首次完成态形成 |

## 6. 仅有部分抓包时可恢复的信息边界

| 抓包内容 | 能恢复的信息 | 不能恢复的信息 |
| --- | --- | --- |
| 仅有 `watchVideo` | 已点开过的 `videoId`、`classId`、`courseId`、`chapterNodeId` | 整门课目录、章节树、完整视频清单 |
| 仅有 MP4 请求 | 已访问过的媒体文件 ID | 对应的课程、小节、学习完成状态 |
| 仅有 `personal/sync` | 当前 section/page/video 的完成状态与观看记录 | 整门课完整目录 |
| 目录接口 + 章节详情接口 | 整门课章节树与视频清单 | 学习完成态与实时观看记录 |

## 7. 推荐抓包方案

### 7.1 目录与资源清单抓包

| 步骤 | 建议操作 |
| --- | --- |
| 1 | 打开课程学习页 |
| 2 | 切换每个章节至少一次 |
| 3 | 保留 `directory` 与 `wholepage/chapter/stu/...` 请求 |

### 7.2 完成态分析抓包

| 步骤 | 建议操作 |
| --- | --- |
| 1 | 确保目标小节初始状态明确 |
| 2 | 从进入页面前开始抓包 |
| 3 | 保留 `initialize`、`item`、`watchVideo`、heartbeat、`personal/sync` 全链路 |
| 4 | 保留首次出现 `complete=1` 的同步包 |

## 8. 当前结论边界

| 问题 | 当前结论 |
| --- | --- |
| 能否恢复整门课目录 | 可以 |
| 能否恢复每个章节下的视频资源 | 可以 |
| 能否确认完成态提交接口 | 可以 |
| 能否确认视频从 0 秒看到尾才完成 | 当前证据不足 |
| 能否确认服务端是否严格校验倍速 | 当前证据不足 |
