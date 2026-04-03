# DGUT Ulearning 视频播放与行为打点接口说明

## 1. 文档范围

本文档说明视频媒体流接口、视频封面接口以及平台行为打点接口，并明确其与学习记录同步接口的区别。

## 2. 视频封面接口

### 2.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 视频封面帧 |
| 方法 | `GET` |
| URL | `/resources/web/<media-id>.mp4?vframe/jpg/offset/1` |
| 域名 | `https://obscloud.ulearning.cn` |

### 2.2 作用说明

| 作用 | 说明 |
| --- | --- |
| 视频预览图 | 获取视频首帧或预览帧 |
| 非正式播放流 | 不参与学习记录统计 |

## 3. 视频媒体流接口

### 3.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 视频 MP4 流 |
| 方法 | `GET` |
| URL | `/resources/web/<media-id>.mp4?token=<token>` |
| 域名 | `https://obscloud.ulearning.cn` |

### 3.2 请求特征

| 项目 | 值 |
| --- | --- |
| 请求模式 | `cors` |
| 常见请求头 | `Range`、`Accept`、`Origin`、`Referer` |
| 鉴权方式 | URL Query 中携带 `token` |
| 响应状态 | `206 Partial Content` |
| 响应类型 | `video/mp4` |

### 3.3 典型样例

| 项目 | 样例值 |
| --- | --- |
| 请求 URL | `https://obscloud.ulearning.cn/resources/web/17405354188653939.mp4?token=...` |
| 请求头 `Range` | `bytes=2079443-` |
| 响应头 `Content-Range` | `bytes 2079443-8707276/8707277` |
| 响应头 `Content-Length` | `6627834` |

### 3.4 结论

| 结论项 | 结果 |
| --- | --- |
| 是否为 HLS | 否 |
| 是否为 MP4 直链 | 是 |
| 是否支持 Range | 是 |
| 是否直接表示学习完成 | 否 |

## 4. 播放行为打点接口

### 4.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 视频播放行为打点 |
| 方法 | `POST` |
| URL | `/courseapi/behavior/watchVideo` |
| 域名 | `https://lms.dgut.edu.cn` |

### 4.2 请求头特征

| 请求头 | 说明 |
| --- | --- |
| `Authorization` | 平台认证头 |
| `Content-Type: application/json` | JSON 请求体 |
| `Origin: https://ua.dgut.edu.cn` | 来自学习页 |
| `Referer: https://ua.dgut.edu.cn/` | 学习页来源 |

### 4.3 请求体结构

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `classId` | Integer | 班级 ID |
| `courseId` | Integer | 课程 ID |
| `chapterId` | Integer | 内部章节节点 ID，不是 URL 中的目录层 `chapterId` |
| `videoId` | Integer | 视频业务 ID |

### 4.4 样例请求体

| 字段 | 样例值 |
| --- | --- |
| `classId` | `944483` |
| `courseId` | `55892` |
| `chapterId` | `2581780` |
| `videoId` | `1717243` |

### 4.5 接口语义

| 问题 | 结论 |
| --- | --- |
| 是否表示开始看某个视频 | 是 |
| 是否表示切换到某个视频 | 是，具备该语义 |
| 是否表示视频播放完成 | 否 |
| 是否承载学习进度 | 否 |

## 5. 视频本地记录模型

页面播放器运行期间，本地维护的视频记录对象通常包含以下字段：

| 字段 | 含义 |
| --- | --- |
| `videoId` | 视频业务 ID |
| `positionTime` | 当前播放位置 |
| `viewTime` | 累计观看时长 |
| `videoDuration` | 视频总时长 |
| `status` | 完成状态 |
| `startEndTimeList` | 实际观看时间段 |
| `maxPositionTime` | 已允许到达的最大播放点 |
| `viewProgress` | 播放进度百分比 |

## 6. 前端播放约束

### 6.1 完成阈值

| 条件 | 结果 |
| --- | --- |
| `viewProgress >= 95` | 将视频视为完成，`status = 1` |

### 6.2 防快进机制

| 条件 | 行为 |
| --- | --- |
| `currentTime > maxPositionTime + 3` 且视频未完成 | 播放器回退到允许位置 |

## 7. 倍速能力说明

### 7.1 前端能力

| 项目 | 结果 |
| --- | --- |
| 前端是否存在倍速功能 | 是 |
| 权限控制字段 | 用户权限 `id == 148` |
| 可见档位 | `0.75`、`1.00`、`1.25`、`1.50`、`2.00` |

### 7.2 当前接口观察结果

| 接口 | 是否发现显式 `speed` 字段 |
| --- | --- |
| `/courseapi/behavior/watchVideo` | 否 |
| `/uaapi/yws/api/personal/sync` | 否 |

### 7.3 说明

虽然当前样本中未发现显式倍速字段，但学习记录中存在：

| 字段 | 说明 |
| --- | --- |
| `recordTime` | 记录累计观看时间 |
| `startEndTimeList` | 记录实际观看时间段 |

因此，当前只能确认“前端支持倍速且未显式上报倍速字段”，不能仅据此判断服务端是否完全不做时长一致性校验。

## 8. 与学习记录同步接口的关系

| 接口 | 职责 |
| --- | --- |
| `/resources/web/<media-id>.mp4?token=...` | 仅负责媒体流传输 |
| `/courseapi/behavior/watchVideo` | 仅负责开始播放行为打点 |
| `/uaapi/yws/api/personal/sync?courseType=4&platform=PC` | 负责真正的学习进度与完成状态提交 |

## 9. 重要结论

| 编号 | 结论 |
| --- | --- |
| 1 | 视频播放接口为 MP4 直链，不是 HLS |
| 2 | `watchVideo` 不是“视频播放完成提交”接口 |
| 3 | 视频完成状态最终体现在 `personal/sync` 的加密包中 |
| 4 | 单独执行一次 MP4 请求，不足以构成完整的学习完成链路 |
