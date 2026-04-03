# DGUT Ulearning 学习记录与同步接口说明

## 1. 文档范围

本文档对 DGUT Ulearning 学习记录链路进行详细说明，覆盖以下内容：

- 学习记录初始化接口
- 学习记录读取接口
- 心跳保活接口
- 学习记录同步接口
- 提交前的前端状态累积逻辑
- 提交加密规则与认证方式
- 完成态判定逻辑
- 典型会话时序与样例解读

本文档关注的是“学习状态如何被记录和提交”，不涉及伪造学习记录或绕过平台校验。

## 2. 记录链路总览

学习记录相关接口并不是孤立存在的，而是构成一条连续链路。

### 2.1 总体链路

| 顺序 | 阶段 | 动作 | 典型接口 |
| --- | --- | --- | --- |
| 1 | 初始化会话 | 为当前小节创建学习会话，获得 `studyStartTime` | `GET /uaapi/studyrecord/initialize/<itemid>` |
| 2 | 恢复历史记录 | 读取当前小节已有学习记录 | `GET /uaapi/studyrecord/item/<itemid>?courseType=4` |
| 3 | 进入学习状态 | 页面与播放器在前端本地累积进度 | 页面本地逻辑 |
| 4 | 心跳保活 | 维持会话并配合防作弊逻辑 | `GET /uaapi/studyrecord/heartbeat/<itemid>/<studyStartTime>` |
| 5 | 组装记录 | 将 section/page/question/video 四层记录组装为同步对象 | `Section.createRecord()` |
| 6 | 加密请求体 | 对 JSON 文本执行 `DES-ECB + PKCS7` 加密 | 页面本地逻辑 |
| 7 | 提交同步 | 将加密后的学习记录提交给服务端 | `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` |

### 2.2 与视频行为接口的关系

| 接口 | 职责 | 是否承载完成状态 |
| --- | --- | --- |
| `/courseapi/behavior/watchVideo` | 开始播放或切换视频时的行为打点 | 否 |
| `/uaapi/studyrecord/heartbeat/...` | 学习会话保活 | 否 |
| `/uaapi/yws/api/personal/sync?courseType=4&platform=PC` | 真正提交学习进度与完成态 | 是 |

## 3. 学习记录初始化接口

### 3.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 学习记录初始化 |
| 方法 | `GET` |
| URL | `/uaapi/studyrecord/initialize/<itemid>` |
| 域名 | `https://ua.dgut.edu.cn` |
| 认证方式 | `AUTHORIZATION`、`UA-AUTHORIZATION` |

### 3.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `itemid` | Integer | 是 | 小节记录 ID |

### 3.3 返回值

| 返回值 | 类型 | 含义 |
| --- | --- | --- |
| `1775131296` | Integer | `studyStartTime`，当前小节学习会话启动时间戳 |

### 3.4 接口作用

| 作用 | 说明 |
| --- | --- |
| 创建学习会话 | 为当前 `itemid` 创建新的学习会话 |
| 生成会话标识 | 返回 `studyStartTime`，供 heartbeat 和 sync 使用 |
| 绑定小节上下文 | 后续所有记录均围绕当前 `itemid + studyStartTime` 展开 |

### 3.5 重要说明

| 事项 | 说明 |
| --- | --- |
| 作用范围 | 初始化的是“小节学习会话”，不是整门课会话 |
| 重复调用 | 切换 section 后通常会重新初始化 |
| 与 heartbeat 的关系 | heartbeat URL 中必须携带同一份 `studyStartTime` |

## 4. 学习记录读取接口

### 4.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 小节学习记录读取 |
| 方法 | `GET` |
| URL | `/uaapi/studyrecord/item/<itemid>?courseType=4` |
| 域名 | `https://ua.dgut.edu.cn` |
| 认证方式 | `AUTHORIZATION`、`UA-AUTHORIZATION` |

### 4.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `itemid` | Integer | 是 | 小节记录 ID |
| Query | `courseType` | Integer | 是 | 当前样本固定为 `4` |

### 4.3 主要用途

| 用途 | 说明 |
| --- | --- |
| 恢复 section 状态 | 恢复当前小节是否已完成 |
| 恢复 page 状态 | 恢复页面得分、完成状态、学习时间 |
| 恢复 video 状态 | 恢复当前播放位置、观看时长、完成状态 |

### 4.4 典型恢复内容

| 层级 | 可恢复信息 |
| --- | --- |
| 小节层 | `complete`、`score`、`studyStartTime` |
| 页面层 | `pageid`、`complete`、`studyTime`、`score` |
| 视频层 | `videoid`、`current`、`status`、`recordTime`、`time`、`startEndTimeList` |

## 5. 心跳保活接口

### 5.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 学习心跳 |
| 方法 | `GET` |
| URL | `/uaapi/studyrecord/heartbeat/<itemid>/<studyStartTime>` |
| 域名 | `https://ua.dgut.edu.cn` |
| 认证方式 | `AUTHORIZATION`、`UA-AUTHORIZATION` |

### 5.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `itemid` | Integer | 是 | 小节记录 ID |
| Path | `studyStartTime` | Integer | 是 | 初始化接口返回的会话时间戳 |

### 5.3 样例返回

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | Integer | 当前样本恒为 `0` |

### 5.4 已验证行为

| 观察项 | 结果 |
| --- | --- |
| 调用周期 | 约每 `100` 秒一次 |
| 完成后是否继续调用 | 是 |
| 典型返回值 | `{"status":0}` |
| 与同步的关系 | 每次同步后约 `2.6` 秒常出现下一次 heartbeat |

### 5.5 说明

| 事项 | 说明 |
| --- | --- |
| 语义 | 更接近“会话保活”和“防作弊保活” |
| 非完成提交 | heartbeat 本身不携带进度详情 |
| 非最终结算 | 即使视频已完成，heartbeat 也可能继续调用 |

## 6. 学习记录同步接口

### 6.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 学习记录同步 |
| 方法 | `POST` |
| URL | `/uaapi/yws/api/personal/sync?courseType=4&platform=PC` |
| 域名 | `https://ua.dgut.edu.cn` |
| 认证方式 | `AUTHORIZATION`、`UA-AUTHORIZATION` |

### 6.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Query | `courseType` | Integer | 是 | 当前样本为 `4` |
| Query | `platform` | String | 是 | 当前样本为 `PC` |
| Body | 加密字符串 | String | 是 | 由明文 JSON 经 DES 加密得到 |

### 6.3 接口职责

| 职责 | 说明 |
| --- | --- |
| 同步学习进度 | 提交 section/page/video 三级学习状态 |
| 同步完成态 | 提交视频完成、页面完成、小节完成 |
| 同步学习时长 | 提交 `studyTime`、`recordTime`、`startEndTimeList` |
| 周期性保存 | 自动保存、手动保存、切换 section、离开页面等场景统一走此接口 |

## 7. 鉴权方式

### 7.1 Token 来源

| 来源 | 说明 |
| --- | --- |
| Cookie `token` | 主要认证来源 |
| Cookie `AUTHORIZATION` | 与 `token` 值一致时可共同使用 |

### 7.2 常见请求头

| 请求头 | 说明 |
| --- | --- |
| `AUTHORIZATION` | UA 学习接口主认证头 |
| `UA-AUTHORIZATION` | UA 学习接口附加认证头 |
| `Content-Type` | 当前样本为 `application/json` |
| `Origin` | 当前样例为 `https://ua.dgut.edu.cn` |
| `Referer` | 当前样例为 `learnCourse.html?...` |

### 7.3 认证说明

| 事项 | 说明 |
| --- | --- |
| UA 业务接口 | 主要依赖 `AUTHORIZATION` 与 `UA-AUTHORIZATION` |
| LMS 行为接口 | 通常使用 `Authorization` |
| `watchVideo` 与 `personal/sync` 区别 | 前者是行为打点，后者是真正学习状态提交 |

## 8. 请求体加密规则

### 8.1 加密参数

| 项目 | 值 |
| --- | --- |
| 算法 | `DES` |
| 模式 | `ECB` |
| Padding | `PKCS7` |
| Key | `12345678` |

### 8.2 加密流程

| 顺序 | 动作 |
| --- | --- |
| 1 | 前端收集当前 section/page/video 的明文记录对象 |
| 2 | 将记录对象序列化为 JSON 文本 |
| 3 | 使用 `DES-ECB + PKCS7 + key=12345678` 对 JSON 文本加密 |
| 4 | 将加密后的字符串作为请求体提交到 `personal/sync` |

### 8.3 解密后数据层次

| 层级 | 对象名称 | 说明 |
| --- | --- | --- |
| 小节层 | `ItemStudyRecordUpdateDTO` | 当前 section 的总记录 |
| 页面层 | `PageStudyRecordDTO` | 当前 section 下每个 page 的记录 |
| 题目层 | `QuestionStudyRecordDTO` | 当前练习页面下每道题的记录 |
| 视频层 | `VideoStudyRecordDTO` | 当前 page 下每个 video 的记录 |

## 9. 解密后顶层结构

### 9.1 小节层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `itemid` | Integer | 小节记录 ID |
| `autoSave` | Integer | 保存方式标记 |
| `withoutOld` | Integer / Null | 额外同步控制字段 |
| `complete` | Integer | 小节是否完成 |
| `studyStartTime` | Integer | 学习会话启动时间 |
| `userName` | String | 用户名 |
| `score` | Number | 小节得分 |
| `pageStudyRecordDTOList` | Array | 页面记录列表 |

### 9.2 页面层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `pageid` | Integer | 页面记录关联 ID |
| `complete` | Integer | 页面是否完成 |
| `studyTime` | Number | 页面学习时长 |
| `score` | Number | 页面得分 |
| `answerTime` | Number | 作答相关计数字段 |
| `submitTimes` | Number | 提交次数 |
| `coursepageId` | Integer | 练习组件 ID，用于恢复本页题目记录 |
| `questions` | Array | 题目记录 |
| `videos` | Array | 视频记录 |
| `speaks` | Array | 口语记录 |

### 9.3 题目层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `questionid` | Integer | 单题 ID |
| `answerList` | Array | 用户本次提交的答案列表 |
| `score` | Number | 该题用户得分 |

### 9.4 视频层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `videoid` | Integer | 视频业务 ID |
| `current` | Number | 当前播放位置 |
| `status` | Integer | 视频完成状态 |
| `recordTime` | Number | 本次累计观看时长 |
| `time` | Number | 视频总时长 |
| `startEndTimeList` | Array | 实际观看时间段列表 |

### 9.5 `startEndTimeList` 结构

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `startTime` | Integer | Unix 时间戳，观看开始时间 |
| `endTime` | Integer | Unix 时间戳，观看结束时间 |

## 10. 前端本地状态是如何累积的

在真正提交前，前端会先本地累积视频页与测试页的学习状态。

### 10.1 关键本地字段

| 字段 | 含义 |
| --- | --- |
| `positionTime` | 当前播放到的视频位置 |
| `viewTime` | 累计有效观看时长 |
| `maxPositionTime` | 已允许到达的最大播放点 |
| `viewProgress` | 当前观看进度百分比 |
| `startEndTimeList` | 实际观看时间段 |

### 10.2 典型更新逻辑

| 动作 | 更新结果 |
| --- | --- |
| 播放进行中 | `positionTime = currentTime` |
| 播放进行中 | `viewTime += addTime` |
| 播放进行中 | `maxPositionTime = max(maxPositionTime, currentTime)` |
| 播放进行中 | `startEndTimeList[last].endTime = now` |
| 达到完成阈值 | `status = 1` |

### 10.3 测试页状态累积逻辑

| 动作 | 更新结果 |
| --- | --- |
| 点击测试页“提交” | 前端先增加 `submitTimes` |
| 单题执行 `submitQuestion()` | 若无现成答案，先调用 `questionAnswer` 拉标准答案 |
| 本地判分 | 浏览器内计算 `answer`、`userScore`、`status` |
| 页面取记录 `Page.getRecord()` | 汇总 `questionRecords`、页面分数、`submitTimes`、`coursepageId` |
| 节点保存 `Section.createRecord()` | 把题目记录序列化进 `pageStudyRecordDTOList[].questions[]` 后统一同步 |

## 11. 完成态判定

### 11.1 前端完成规则

| 条件 | 行为 |
| --- | --- |
| `viewProgress >= 95` | 前端将视频 `status` 置为 `1` |

### 11.2 三层完成态的关系

| 层级 | 完成条件 | 完成态字段 |
| --- | --- | --- |
| 视频层 | 视频进度达到阈值 | `videos[].status = 1` |
| 页面层 | 页面内视频或题目达成完成条件 | `page.complete = 1` |
| 小节层 | 当前小节下所有页面完成 | `section.complete = 1` |

### 11.3 已验证完成态特征

| 层级 | 字段 | 完成态表现 |
| --- | --- | --- |
| 小节层 | `complete` | `1` |
| 页面层 | `complete` | `1` |
| 视频层 | `status` | `1` |
| 视频层 | `current` | 常见为 `0` |

## 12. 同步触发时机

### 12.1 触发矩阵

| 场景 | 是否触发 `createRecord()` | 说明 |
| --- | --- | --- |
| 切换 section 前 | 是 | 保存旧 section 的学习记录 |
| 定时自动保存 | 是 | 默认约每 `5` 分钟一次 |
| 手动保存进度 | 是 | 用户主动触发 |
| 当前 section 全部完成 | 是 | 触发完成态提交 |
| 打开统计页 | 是 | 进入统计相关页面前保存 |
| 关闭页面或返回上层 | 是 | 退出前兜底保存 |

### 12.2 自动保存周期

| 运行环境 | 周期 |
| --- | --- |
| PC 网页端 | 约 `5 * 60 * 1000` 毫秒 |
| 小程序模式 | 约 `20 * 1000` 毫秒 |

### 12.3 测试页补充说明

| 事项 | 说明 |
| --- | --- |
| 点击“提交”是否立即发最终请求 | 从 PC 网页端源码看，不会直接发 `personal/sync` |
| 测试结果何时真正落库 | 由后续 `createRecord()` 统一提交 |
| 测试结果落在哪些字段 | `score`、`submitTimes`、`coursepageId`、`questions[]` |
| 已有 HAR 证据 | `2026-04-03 11:20:37` 已抓到测试页离页前的真实 `personal/sync` |
| 未成形答案的表现 | 若题目答案仍是 `null` / `undefined`，该题不会进入 `questions[]` |

### 12.4 `2026-04-03 14:32` 即时出分实测

针对以下页面入口做了直接实测：

```text
https://ua.dgut.edu.cn/learnCourse/learnCourse.html?courseId=60251&chapterId=136356084&classId=941992&returnUrl=https%3A%2F%2Flms.dgut.edu.cn%2Fcourseweb%2Fulearning%2Findex.html%23%2Fcourse%2Ftextbook%3FcourseId%3D159530
```

映射后的关键对象为：

| 字段 | 实测值 |
| --- | --- |
| `chapterNodeId` | `2602181` |
| `itemid` | `2773463` |
| 测试页数 | `7` |
| 题目总数 | `65` |

实测顺序：

1. 读取 `studyrecord/item/2773463?courseType=4`，基线 `score=0`。
2. 读取章节内容并解析出 `65` 道题。
3. 调用 `questionAnswer` 取回全部标准答案。
4. 构造 `pageStudyRecordDTOList`，提交总分 `score=65`。
5. 直接调用 `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC`。
6. 不切页、不退出，立刻再次调用 `studyrecord/item/2773463?courseType=4`。

实测结果：

| 观察项 | 结果 |
| --- | --- |
| 同步接口返回 | `1` |
| 提交前小节得分 | `0` |
| 提交后首次回读小节得分 | `65` |
| 提交后首次回读页面记录数 | `8` |
| 首次回读是否已包含 `questions[]` 明细 | 是 |

这条实测说明：

| 结论 | 说明 |
| --- | --- |
| `personal/sync` 足以让测试页分数立刻可读 | 是 |
| “必须退出题目界面后才有分数”是否成立 | 否，至少在该样例中不成立 |
| 真正关键步骤 | 不是 `refresh10Session` / `isValidToken`，而是把题目记录提交到 `personal/sync` |

## 13. 已验证会话样例

基于 `2026-04-02 20:49:55` 的单视频会话 HAR，可确认：

| 观察项 | 结果 |
| --- | --- |
| `personal/sync` 次数 | `3` 次 |
| 同步间隔 | 约 `300` 秒 |
| 第一次同步是否已完成 | 是 |
| 完成后是否继续同步 | 是 |
| 完成后是否继续 heartbeat | 是 |

### 13.1 会话时间线

| 时间 | 事件 |
| --- | --- |
| `20:49:25` | 请求 MP4 数据 |
| `20:49:26` | `watchVideo` 行为打点 |
| `20:50:18` | 第 1 次 heartbeat |
| `20:51:58` | 第 2 次 heartbeat |
| `20:53:35` | 第 1 次 `personal/sync`，已是完成态 |
| `20:58:35` | 第 2 次 `personal/sync`，重复保存完成态 |
| `21:03:35` | 第 3 次 `personal/sync`，重复保存完成态 |

## 14. 解密样例解读

### 14.1 完成态样例

```json
{
  "itemid": 2584634,
  "autoSave": 1,
  "withoutOld": null,
  "complete": 1,
  "studyStartTime": 1775134119,
  "userName": "<USER_NAME>",
  "score": 100,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2584635,
      "complete": 1,
      "studyTime": 298,
      "score": 100,
      "videos": [
        {
          "videoid": 1717243,
          "current": 0,
          "status": 1,
          "recordTime": 174.480233,
          "time": 214.480233,
          "startEndTimeList": [
            {
              "startTime": 1775134165,
              "endTime": 1775134187
            }
          ]
        }
      ]
    }
  ]
}
```

### 14.2 样例解读

| 字段 | 样例值 | 解释 |
| --- | --- | --- |
| `complete` | `1` | 当前小节已完成 |
| `pageStudyRecordDTOList[0].complete` | `1` | 当前页面已完成 |
| `videos[0].status` | `1` | 当前视频已完成 |
| `videos[0].current` | `0` | 提交时当前播放位置已归零或不再保留中间位置 |
| `videos[0].recordTime` | `174.480233` | 本次累计记录的观看时长 |
| `videos[0].time` | `214.480233` | 视频总时长 |
| `startEndTimeList` | 一段时间区间 | 记录本次实际观看发生的真实时间段 |

## 15. `watchVideo` 与 `personal/sync` 的区别

| 比较项 | `watchVideo` | `personal/sync` |
| --- | --- | --- |
| 域名 | `lms.dgut.edu.cn` | `ua.dgut.edu.cn` |
| 接口定位 | 行为打点 | 学习状态同步 |
| 是否提交完成态 | 否 | 是 |
| 是否包含 `videoId` | 是 | 是 |
| 是否包含 `recordTime` | 否 | 是 |
| 是否包含 `startEndTimeList` | 否 | 是 |
| 是否包含 `complete` | 否 | 是 |

## 16. 当前证据已经能证明什么

| 编号 | 已证实结论 |
| --- | --- |
| 1 | 真正的完成提交接口是 `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` |
| 2 | 提交前前端会执行 `DES-ECB + PKCS7 + key=12345678` 加密 |
| 3 | 鉴权主要依赖 `AUTHORIZATION` 与 `UA-AUTHORIZATION` |
| 4 | 同步数据中同时包含小节、页面、题目、视频四层状态 |
| 5 | 测试页答题结果不是单独接口落库，而是进入 `pageStudyRecordDTOList[].questions[]` 统一同步 |
| 6 | heartbeat 与 sync 都围绕 `itemid + studyStartTime` 工作 |
| 7 | `submitTimes` 与 `coursepageId` 也是测试页持久化记录的一部分 |
| 8 | 测试页切页/离页时，前端会把当前题目状态作为默认学习进度同步到 `personal/sync` |
| 9 | `complete=1` 不等于得分大于 0，二者在测试页同步包中可以分离出现 |

## 17. 当前仍不能直接证明的部分

| 问题 | 当前结论 |
| --- | --- |
| 后端是否严格比对 `recordTime` 与 `startEndTimeList` | 证据不足 |
| 后端是否对异常倍速或异常时间跨度做额外校验 | 证据不足 |
| `autoSave`、`withoutOld` 的全部语义是否已完全还原 | 仅能部分解释 |

## 18. 参考文档

| 文档 | 内容 |
| --- | --- |
| `04-api-video-playback-and-behavior.md` | 视频播放与行为打点接口 |
| `06-api-request-and-response-examples.md` | 请求与响应样例 |
| `07-api-field-dictionary-and-id-mapping.md` | 字段字典与 ID 映射 |
| `08-api-session-timeline-and-capture-requirements.md` | 会话时序与抓包要求 |

