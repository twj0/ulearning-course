# DGUT Ulearning 测试页与题目答案接口说明

## 1. 文档范围

本文档用于补充课程测试页相关接口，重点说明：

- 测试页在课程章节中的对象结构
- `questionid`、`pageId`、`relationid`、`itemid` 之间的关系
- `GET /uaapi/questionAnswer/<questionid>?parentId=<pageId>` 的调用方式
- `2026-04-03 10:27:19` HAR 所反映出的“视频页收尾 -> 测试页初始化 -> 拉答案”时序
- 题目答案接口是否存在额外加密、签名或实名字段要求
- 测试页点击“提交”后，前端本地评分与服务端持久化分别落在哪一层
- 题目作答结果、得分、提交次数最终写入哪个 UA 接口与字段

本文档对应的主要样本来源：

- `developer/network/ua.dgut.edu.cn_Archive [26-04-03 10-27-19].har`
- `developer/network/ua.dgut.edu.cn_Archive [26-04-03 11-20-37].har`
- `userscripts/get-question-train.js`
- `userscripts/helper.js`
- UA 前端源码：
  - `https://ua.dgut.edu.cn/learnCourse/js/model/Section.js?version=250114`
  - `https://ua.dgut.edu.cn/learnCourse/js/model/Page.js?version=250114`
  - `https://ua.dgut.edu.cn/learnCourse/js/model/Question.js?version=250114`
  - `https://ua.dgut.edu.cn/learnCourse/components/questionView/questionViewModel.js?version=250114`
  - `https://ua.dgut.edu.cn/learnCourse/components/questionElementView/questionElementViewModel.js?version=250114`

## 2. 测试页在课程模型中的位置

课程 `55892` 第一章中，除视频小节外，还存在一个测试小节：

| 层级 | 字段 | 值 | 说明 |
| --- | --- | --- | --- |
| 课程层 | `courseId` | `55892` | UA 侧教材 ID |
| 班级层 | `classId` | `944483` | 班级 ID |
| 章节层 | `chapterIdForClass` | `136397207` | 学习页 URL 中的第一章目录 ID |
| 章节层 | `chapterNodeId` | `2581780` | 章节内部节点 ID |
| 小节层 | `itemid` | `2693412` | 第一章测试的小节记录 ID |
| 页面对象层 | `pageId` | `7023243` | 第一章测试的页面对象 ID |
| 页面记录层 | `relationid` | `2693413` | 第一章测试的页面记录关联 ID |

### 2.1 章节内容接口中的测试页样例

从 `GET /uaapi/wholepage/chapter/stu/2581780` 可观察到：

```json
{
  "itemid": 2693412,
  "wholepageDTOList": [
    {
      "contentType": 7,
      "id": 7023243,
      "content": "第一章测试",
      "relationid": 2693413,
      "coursepageDTOList": [
        {
          "type": 6,
          "parentid": 7023243,
          "questionDTOList": [
            {
              "questionid": 18692023,
              "type": 1,
              "title": "<p>直升机的飞行原理来源于：&zwnj;</p>"
            }
          ]
        }
      ]
    }
  ]
}
```

### 2.2 结构结论

| 编号 | 结论 |
| --- | --- |
| 1 | 测试页的 `contentType = 7` |
| 2 | 测试组件的 `type = 6` |
| 3 | `questionDTOList` 中提供题目结构、题干、选项等静态信息 |
| 4 | `questionid` 来自章节内容接口，不在学习记录接口中生成 |
| 5 | 测试页答案接口使用的是页面对象 ID `pageId`，不是学习记录里的 `relationid` |

## 3. 题目答案接口

### 3.1 接口定义

| 项目 | 内容 |
| --- | --- |
| 接口名称 | 题目答案查询 |
| 方法 | `GET` |
| URL | `/uaapi/questionAnswer/<questionid>?parentId=<pageId>` |
| 域名 | `https://ua.dgut.edu.cn` |
| 认证方式 | `AUTHORIZATION`、`UA-AUTHORIZATION` |

### 3.2 请求参数

| 参数位置 | 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | `questionid` | Integer | 是 | 单题 ID |
| Query | `parentId` | Integer | 是 | 测试页页面对象 ID，即 `pageId` |

### 3.3 样例请求

```text
GET https://ua.dgut.edu.cn/uaapi/questionAnswer/18692023?parentId=7023243
```

### 3.4 样例响应

```json
{
  "questionid": 18692023,
  "correctreply": "",
  "correctAnswerList": ["D"]
}
```

### 3.5 已观察到的返回形式

| 题型 | 样例题号 | `correctAnswerList` 样例 |
| --- | --- | --- |
| 单选题 | `18692023` | `["D"]` |
| 单选题 | `18692025` | `["A"]` |
| 单选题 | `18692030` | `["C"]` |
| 判断题 | `18692033` | `["false"]` |
| 判断题 | `18692035` | `["true"]` |

### 3.6 接口语义

| 问题 | 结论 |
| --- | --- |
| 是否直接返回标准答案 | 是 |
| 是否需要 DES 加密请求体 | 否，当前样本中是普通 `GET` |
| 是否需要额外签名参数 | 当前样本中未观察到 |
| 是否需要 `userName` | 当前样本中未观察到 |

## 4. ID 关系补充

测试页相关 ID 与学习记录相关 ID 不能混用：

| 场景 | 字段 | 样例值 | 实际语义 |
| --- | --- | --- | --- |
| 测试页答案接口 | `parentId` | `7023243` | 页面对象 ID，即 `pageId` |
| 学习记录同步接口 | `pageid` | `2693413` | 页面记录关联 ID，即 `relationid` |
| 学习记录初始化/心跳 | `itemid` | `2693412` | 测试小节 ID |
| 题目详情/答案 | `questionid` | `18692023` | 单题 ID |

### 4.1 关键结论

| 编号 | 结论 |
| --- | --- |
| 1 | `questionAnswer` 的 `parentId` 对应的是页面对象 ID |
| 2 | `relationid` 仍然只用于学习记录恢复与同步 |
| 3 | `itemid` 用于测试页学习会话初始化与心跳 |
| 4 | 一个测试页可包含多个 `questionid` |

## 5. `2026-04-03 10:27:19` HAR 时序解读

该 HAR 共 `13` 个请求，全部位于 `ua.dgut.edu.cn`，未包含目录接口、章节详情接口、LMS `watchVideo` 或 MP4 资源请求。

### 5.1 请求顺序

| 顺序 | 时间 | 请求 | 说明 |
| --- | --- | --- | --- |
| 1 | `10:25:07` | `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` | 保存上一个视频页的学习记录 |
| 2 | `10:25:08` | `GET /uaapi/studyrecord/initialize/2693412` | 初始化“第一章测试”的学习会话 |
| 3 | `10:26:48` | `GET /uaapi/studyrecord/heartbeat/2693412/1775183110` | 第一章测试页心跳保活 |
| 4 | `10:27:04` | 连续 `10` 个 `GET /uaapi/questionAnswer/...` | 拉取第一章测试中每道题的标准答案 |

### 5.2 这条时序说明了什么

| 编号 | 结论 |
| --- | --- |
| 1 | 页面切换时，前一个视频页会先触发一次 `personal/sync` |
| 2 | 进入测试页后，依然存在与视频页相同的 `initialize -> heartbeat` 学习会话链路 |
| 3 | 标准答案请求发生在测试页初始化之后 |
| 4 | 题目答案接口与学习记录同步接口是两条独立链路 |

### 5.3 `studyStartTime` 不一致并不冲突

HAR 中：

- 视频页同步包中的 `studyStartTime = 1775183104`
- 测试页初始化返回 `studyStartTime = 1775183110`

这说明：

| 对象 | `studyStartTime` | 含义 |
| --- | --- | --- |
| 视频页 `itemid=2584634` | `1775183104` | 上一个视频页的小节会话 |
| 测试页 `itemid=2693412` | `1775183110` | 新进入测试页的小节会话 |

因此，这是“旧页保存 + 新页初始化”的正常现象，不是同一个页面的冲突值。

## 6. 与学习记录同步接口的关系

HAR 中唯一一条 `personal/sync` 请求解密后为：

```json
{
  "itemid": 2584634,
  "autoSave": 0,
  "withoutOld": null,
  "complete": 1,
  "studyStartTime": 1775183104,
  "userName": "username",
  "score": 100,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2584635,
      "complete": 1,
      "studyTime": 5,
      "score": 100,
      "answerTime": 1,
      "submitTimes": 0,
      "questions": [],
      "videos": [
        {
          "videoid": 1717243,
          "current": 0,
          "status": 1,
          "recordTime": 0,
          "time": 214,
          "startEndTimeList": []
        }
      ],
      "speaks": []
    }
  ]
}
```

### 6.1 可确认的信息

| 观察项 | 结果 |
| --- | --- |
| 此同步包属于哪个页面 | 第一章第一节视频页，不是测试页 |
| 是否携带 `userName` | 是，浏览器样本中携带了 |
| `recordTime = 0` 是否仍可能成功 | 是，当前样本返回 `1` |
| `startEndTimeList` 为空是否仍可能成功 | 是，当前样本返回 `1` |

### 6.2 不能直接推出的结论

| 问题 | 当前结论 |
| --- | --- |
| `userName` 是否为必填 | 不能证明 |
| `userName` 是否必须与实名完全匹配 | 不能证明 |
| 仅凭这一个 HAR 是否能单独证明测试页提交细节 | 不能，需要结合前端源码与真实 `studyrecord` |

### 6.3 前端源码中的答题与提交分工

结合 UA PC 网页端源码，可将测试页流程拆成三层：

| 层级 | 位置 | 关键行为 | 结论 |
| --- | --- | --- | --- |
| 答案获取层 | `Question.getQuestionAnswer()` | `GET /uaapi/questionAnswer/<questionid>?parentId=<pageId>` | 只负责把标准答案拉回前端 |
| 本地判分层 | `questionElementViewModel.submitQuestion()` + `judgeResult()` | 取回标准答案后在浏览器里计算 `answer`、`userScore`、`status` | 点击“提交”本身并没有直接发最终提交请求 |
| 持久化层 | `Section.createRecord()` | 把 `submitTimes`、`coursepageId`、`questions[]` 装入 `ItemStudyRecordUpdateDTO`，DES 加密后 `POST /uaapi/yws/api/personal/sync` | 真正写回服务器的是 `personal/sync` |

其中可以直接对应到的源码行为如下：

| 位置 | 已确认行为 |
| --- | --- |
| `questionViewModel.submitQuiz()` | 只会增加 `usedSubmitChance`、`submitTimes`，然后循环调用每道题的 `submitQuestion()` |
| `questionElementViewModel.submitQuestion()` | 若没有现成答案，则先调用 `getQuestionAnswer()`，再执行 `judgeResult()` |
| `Page.getRecord()` | 从题目组件收集 `questionRecords`，累计页面得分，记录 `submitTimes` |
| `Page.adaptRecord()` | 从历史记录中恢复 `questions`、`submitTimes`、`coursepageId` |
| `Section.createRecord()` | 序列化 `questionid`、`answerList`、`score` 到 `pageStudyRecordDTOList[].questions[]`，然后统一提交到 `personal/sync` |

### 6.4 真实 `studyrecord` 返回值中的题目记录证据

对测试小节 `itemid=2693412` 调用 `GET /uaapi/studyrecord/item/2693412?courseType=4`，已观察到服务端返回：

```json
{
  "completion_status": 1,
  "learner_name": "username",
  "activity_title": "第一章测试",
  "item_id": 2693412,
  "score": 90,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2693413,
      "complete": 1,
      "submitTimes": 1,
      "studyTime": 2144,
      "answerTime": 1,
      "coursepageId": 7024037,
      "questions": [
        {
          "questionid": 18692023,
          "answerList": ["D"],
          "score": 1.0
        },
        {
          "questionid": 18692035,
          "answerList": ["false"],
          "score": 0.0
        }
      ]
    }
  ]
}
```

这条真实记录说明：

| 观察项 | 结果 |
| --- | --- |
| 题目作答结果是否会落库 | 会，落在 `pageStudyRecordDTOList[].questions[]` |
| 页面得分是否会落库 | 会，落在页面层 `score` 与小节层 `score` |
| 提交次数是否会落库 | 会，落在 `submitTimes` |
| 练习组件 ID 是否会落库 | 会，落在 `coursepageId` |
| 这些结果最终是否能被服务端重新读回 | 会，可由 `studyrecord/item/<itemid>` 恢复 |

### 6.5 `2026-04-03 11:20:37` HAR：点击提交后再切页时的真实同步链路

这份 HAR 把“测试页点击提交后，真正同步落在哪个请求上”补成了直接证据。

#### 6.5.1 请求顺序

| 顺序 | 时间 | 请求 | 说明 |
| --- | --- | --- | --- |
| 1-5 | `11:20:10` | 连续 `5` 个 `GET /uaapi/questionAnswer/...` | 当前测试页拉标准答案 |
| 6-12 | `11:20:14` | `GET /wholepage/chapter/stu/...`、`POST /user/currentUnit`、多个 `GET /studyrecord/item/...` | 页面开始切换章节并恢复目标章节记录 |
| 13 | `11:20:18` | `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` | 把刚才测试页的题目结果同步到服务端 |
| 14 | `11:20:19` | `GET /uaapi/studyrecord/initialize/2773393` | 为新小节创建学习会话 |
| 15-19 | `11:20:22` | 连续 `5` 个 `GET /uaapi/questionAnswer/...` | 下一个测试页再次拉答案 |
| 20-28 | `11:20:24` | 新章节详情与多个 `studyrecord/item` | 继续切换与恢复 |
| 29-30 | `11:20:31`、`11:20:34` | 两次 `POST /uaapi/yws/api/personal/sync` | 新测试页的题目状态再次被同步 |
| 31 | `11:20:34` | `GET /uaapi/studyrecord/initialize/2773395` | 再次进入新小节 |

#### 6.5.2 第 13 个 `personal/sync` 解密结果

```json
{
  "itemid": 2773380,
  "autoSave": 0,
  "withoutOld": 1,
  "complete": 1,
  "studyStartTime": 1775186156,
  "userName": "username",
  "score": 0,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2773381,
      "complete": 1,
      "studyTime": 264,
      "score": 0,
      "answerTime": 1,
      "submitTimes": 2,
      "coursepageId": 7242129,
      "questions": [
        { "questionid": 19548732, "answerList": ["B"], "score": 0 },
        { "questionid": 19548733, "answerList": [], "score": 0 },
        { "questionid": 19548734, "answerList": ["C"], "score": 0 },
        { "questionid": 19548735, "answerList": ["D"], "score": 0 }
      ],
      "videos": [],
      "speaks": []
    }
  ]
}
```

#### 6.5.3 第 29、30 个 `personal/sync` 解密结果

第 29 个同步包：

```json
{
  "itemid": 2773393,
  "autoSave": 1,
  "withoutOld": 1,
  "complete": 1,
  "studyStartTime": 1775186421,
  "userName": "username",
  "score": 0,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2773394,
      "complete": 1,
      "studyTime": 11,
      "score": 0,
      "answerTime": 1,
      "submitTimes": 1,
      "coursepageId": 7242131,
      "questions": [
        { "questionid": 19548737, "answerList": [], "score": 0 },
        { "questionid": 19548738, "answerList": [], "score": 0 },
        { "questionid": 19548739, "answerList": [], "score": 0 },
        { "questionid": 19548740, "answerList": [], "score": 0 }
      ],
      "videos": [],
      "speaks": []
    }
  ]
}
```

第 30 个同步包：

```json
{
  "itemid": 2773393,
  "autoSave": 0,
  "withoutOld": 1,
  "complete": 1,
  "studyStartTime": 1775186421,
  "userName": "username",
  "score": 0,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2773394,
      "complete": 1,
      "studyTime": 0,
      "score": 0,
      "answerTime": 1,
      "submitTimes": 0,
      "coursepageId": 7242131,
      "questions": [
        { "questionid": 19548737, "answerList": [], "score": 0 },
        { "questionid": 19548738, "answerList": [], "score": 0 },
        { "questionid": 19548739, "answerList": [], "score": 0 },
        { "questionid": 19548740, "answerList": [], "score": 0 }
      ],
      "videos": [],
      "speaks": []
    }
  ]
}
```

#### 6.5.4 这份 HAR 的结论

| 观察项 | 结果 |
| --- | --- |
| 点击测试页提交后是否只有 `questionAnswer` | 否，后续确实出现了测试页 `personal/sync` |
| 测试页结果最终是否进入 `personal/sync` | 是，已由解密包直接证实 |
| `questions[]`、`submitTimes`、`coursepageId` 是否真实出现在提交包中 | 是 |
| `complete=1` 是否等于题目答对 | 否，样本中可出现 `complete=1` 但 `score=0` |
| 同一测试页是否可能出现多次同步 | 是，样本中同一 `itemid=2773393` 连续出现 `autoSave=1` 与 `autoSave=0` 两次同步 |

#### 6.5.5 “拉了 5 题答案，但只同步了 4 题”的解释

样本中出现了：

- 先抓到 `5` 次 `questionAnswer`
- 但 `personal/sync` 的 `questions[]` 里只出现 `4` 题

这与前端源码一致，`Section.createRecord()` 在序列化题目时会跳过：

```javascript
if (answer == null || answer == "undefined") {
  continue;
}
```

因此，这更像是：

| 情况 | 是否进入 `questions[]` |
| --- | --- |
| 用户答案已形成，例如 `["B"]` 或 `[]` | 会 |
| 用户答案仍是 `null` / `undefined` | 不会 |

也就是说，第 5 题很可能只是“标准答案已拉回前端，但用户答案对象还没有形成”，所以没有写进同步包。

### 6.6 `2026-04-03 14:32` 针对 `courseId=60251` 的即时出分实测

这次改用一个真实的课程学习页入口做直接验证：

```text
https://ua.dgut.edu.cn/learnCourse/learnCourse.html?courseId=60251&chapterId=136356084&classId=941992&returnUrl=https%3A%2F%2Flms.dgut.edu.cn%2Fcourseweb%2Fulearning%2Findex.html%23%2Fcourse%2Ftextbook%3FcourseId%3D159530
```

通过 `GET /uaapi/course/stu/60251/directory?classId=941992` 可映射出：

| 字段 | 实测值 | 说明 |
| --- | --- | --- |
| URL `chapterId` | `136356084` | 目录层章节 ID |
| `chapterNodeId` | `2602181` | 章节详情接口使用的内部节点 ID |
| `itemid` | `2773463` | 目标小节 |
| 测试页数量 | `7` | 该小节下共有 `7` 个测试页 |

对 `chapterNodeId=2602181` 的章节内容解析后，得到：

| 页面 `coursepageId` | 题目数 | 题型 |
| --- | --- | --- |
| `7242258` | `10` | 单选 |
| `7242259` | `10` | 单选 |
| `7242698` | `10` | 单选 |
| `7242704` | `10` | 单选 |
| `7242709` | `10` | 单选 + 多选 |
| `7242712` | `10` | 多选 |
| `7242715` | `5` | 多选 |

共计 `65` 题。实测过程如下：

1. 先读 `GET /uaapi/studyrecord/item/2773463?courseType=4`，基线记录显示小节 `score=0`。
2. 对全部 `65` 题调用 `GET /uaapi/questionAnswer/<questionid>?parentId=<pageId>`，取回标准答案。
3. 本地按题构造 `questions[]` 与页面 `score`，总分为 `65`。
4. 调用 `GET /uaapi/studyrecord/initialize/2773463` 获取新的 `studyStartTime`。
5. 直接提交 `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC`。
6. 不切页、不退出，立刻再次读取 `studyrecord/item/2773463?courseType=4`。

实测结果：

| 观察项 | 结果 |
| --- | --- |
| 提交前 `score` | `0` |
| 提交包总分 | `65` |
| `personal/sync` 返回值 | `1` |
| 提交后首次回读 `score` | `65` |
| 首次回读 `pageStudyRecordDTOList` 数量 | `8` |
| 首次回读是否已有题目明细 | 是 |

其中，首次回读时已经能直接看到新写入的题目结果，例如：

- `coursepageId=7242258` 已带回 `10` 道题的 `questionid / answerList / score`
- 后续 `7242259 / 7242698 / 7242704 / 7242709 / 7242712 / 7242715` 也都已带回对应题目明细

这条实测给出的结论是：

| 结论 | 说明 |
| --- | --- |
| 课程测试页能否“答题并获得分数” | 能 |
| 是否必须退出题目界面后才出现分数 | 不必须 |
| 让分数出现的关键动作 | 将题目记录提交到 `personal/sync` |
| `refresh10Session` / `isValidToken` 是否负责出分 | 否 |

### 6.7 `2026-04-03 15:xx` 多测试小节章节的整章提交流程实测

仅验证“单个测试小节能立刻出分”还不够，因为一个目录层 `chapterId` 下面可能挂着多个测试小节。若 CLI 只提交第一个小节，就会出现：

- 命令输出看似成功
- 某一个 `itemid` 的分数已经写入
- 但课程页面整体进度仍停在中间值，例如 `50%`

以以下真实学习页入口为例：

```text
https://ua.dgut.edu.cn/learnCourse/learnCourse.html?courseId=60251&chapterId=136356088&classId=941992&returnUrl=https%3A%2F%2Flms.dgut.edu.cn%2Fcourseweb%2Fulearning%2Findex.html%23%2Fcourse%2Ftextbook%3FcourseId%3D159530
```

通过 `GET /uaapi/course/stu/60251/directory?classId=941992` 可确认：

| 字段 | 实测值 | 说明 |
| --- | --- | --- |
| URL `chapterId` | `136356088` | 目录层章节 ID |
| `chapterNodeId` | `2602225` | 章节详情接口使用的内部节点 ID |
| 测试小节 1 `itemid` | `2773645` | 已有 `23` 分 |
| 测试小节 2 `itemid` | `2773786` | 初始 `0` 分 |

进一步解析 `GET /uaapi/wholepage/chapter/stu/2602225` 可得到：

| `itemid` | 标题 | 测试页数 | 题目总数 |
| --- | --- | --- | --- |
| `2773645` | 中国共产党第二十届中央委员会第四次全体会议公报 | `3` | `23` |
| `2773786` | 中共中央关于制定国民经济和社会发展第十五个五年规划的建议 | `6` | `47` |

因此，该 `chapterId` 实际上对应的是“一个章节、两个测试小节”。如果只提交第一个 `itemid=2773645`，看到的现象就会是：

| 观察项 | 结果 |
| --- | --- |
| 第一个小节是否有分数 | 是，`23` |
| 第二个小节是否仍未完成 | 是，`0` |
| 章节整体进度是否可能仍停在中间值 | 是 |

对这个章节执行“整章遍历全部测试小节”的提交后，实测结果为：

| 观察项 | 结果 |
| --- | --- |
| 章节内测试小节数 | `2` |
| 测试页总数 | `9` |
| 题目总数 | `70` |
| 提交前总分 | `23` |
| 提交后总分 | `70` |
| 首次回读总分 | `70` |
| 小节 1 首次回读 | `23` |
| 小节 2 首次回读 | `47` |

这条实测说明：

| 结论 | 说明 |
| --- | --- |
| `chapterId` 是否只对应一个测试小节 | 不一定 |
| CLI 的章节模式应如何处理 | 应遍历该章节下全部测试小节 |
| “命令成功但进度仍是 50%” 的根因 | 往往不是延迟，而是章节下还有未提交的小节 |

## 7. 关于加密、签名与用户脚本的结论

### 7.1 UA 课程测试页答案接口

当前已观察到：

| 项目 | 结论 |
| --- | --- |
| 请求方法 | 普通 `GET` |
| 请求体 | 无 |
| 额外加密 | 未观察到 |
| 额外签名 | 未观察到 |
| 返回内容 | 直接包含 `correctAnswerList` |

因此，现阶段没有证据表明 `questionAnswer` 本身需要 DES 加密或额外签名。

### 7.2 `userscripts/get-question-train.js`

该脚本对应的是另一套题库训练系统：

| 项目 | 内容 |
| --- | --- |
| 目标页面 | `https://lms.dgut.edu.cn/utest/index.html*` |
| API 基础路径 | `https://lms.dgut.edu.cn/utestapi` |
| 典型接口 | `/questionTraining/student/answerSheet`、`/questionTraining/student/questionList`、`/questionTraining/student/answer` |
| 认证方式 | `Authorization` 头 + Cookie |

该脚本通过向 `utestapi` 提交一个“占位答案”，再从响应中的 `correctAnswer` 提取标准答案。

结论：

| 编号 | 结论 |
| --- | --- |
| 1 | `get-question-train.js` 不属于 UA 课程测试页接口体系 |
| 2 | 它说明平台内部至少存在第二套题目系统 |
| 3 | 它不能直接证明 UA `questionAnswer` 需要加密或提交答案换取标准答案 |

### 7.3 `userscripts/helper.js`

`helper.js` 中存在如下逻辑：

```javascript
$.get('https://api.ulearning.cn/questionAnswer/' + this.questionId + '?parentId=' + this.parentId, function(xhr) {
  res_answer = xhr;
})
```

该逻辑与本次 HAR 观察到的 `GET /uaapi/questionAnswer/<questionid>?parentId=<pageId>` 在接口语义上高度一致，说明：

| 观察项 | 结果 |
| --- | --- |
| 老脚本是否也把答案接口当普通 GET 使用 | 是 |
| 老脚本中是否出现答案接口加密逻辑 | 否 |
| 老脚本是否出现题目答案接口实名字段 | 否 |

## 8. 当前证据已经能证明什么

| 编号 | 已证实结论 |
| --- | --- |
| 1 | 课程测试页的题目结构来自章节内容接口中的 `questionDTOList` |
| 2 | 课程测试页标准答案可通过 `GET /uaapi/questionAnswer/<questionid>?parentId=<pageId>` 读取 |
| 3 | 该接口中的 `parentId` 对应页面对象 ID，不是学习记录 `relationid` |
| 4 | 当前样本中未发现题目答案接口的加密、签名或 `userName` 要求 |
| 5 | 测试页也存在 `initialize -> heartbeat` 的学习会话链路 |
| 6 | 测试页点击“提交”时，前端先在本地完成判分，不是立刻走独立的“交卷接口” |
| 7 | UA 课程测试页真正的服务端持久化通道是 `POST /uaapi/yws/api/personal/sync?courseType=4&platform=PC` |
| 8 | 题目答案、题目得分、页面得分、提交次数最终会写入 `pageStudyRecordDTOList[].questions[]`、`score`、`submitTimes`、`coursepageId` |
| 9 | `GET /uaapi/studyrecord/item/<itemid>?courseType=4` 能把上述测试结果再完整恢复回来 |
| 10 | `2026-04-03 11:20:37` HAR 已直接抓到测试页的 `personal/sync`，不再只是源码推断 |
| 11 | 测试页切页/离页时，确实会把当前答题状态作为默认学习进度同步出去 |
| 12 | `complete=1` 与 `score>0` 不是同一概念；测试页里可出现“完成同步但得分为 0” |

## 9. 当前仍不能直接证明的部分

| 问题 | 当前结论 |
| --- | --- |
| “点击提交”按钮本身是否会立即触发一次同步 | 当前 HAR 更像“点击提交后，再切页/离页触发同步”，尚未单独抓到“只点提交不跳转”的即时同步 |
| APP / 小程序端是否完全复用同一套测试提交流程 | 当前结论主要基于 PC 网页端源码 |
| 服务端是否会对 `questions[]`、`submitTimes`、`score` 做额外一致性校验 | 证据不足 |
| 是否存在“仅老师开放时才返回标准答案”的额外权限条件 | 证据不足 |

## 10. 参考文档

| 文档 | 内容 |
| --- | --- |
| `02-api-course-directory-and-content.md` | 课程目录、页面对象、测试页结构 |
| `03-api-study-record-and-sync.md` | 学习会话、心跳、同步加密规则 |
| `06-api-request-and-response-examples.md` | 接口请求与响应样例 |
| `07-api-field-dictionary-and-id-mapping.md` | 各类 ID 的上下文映射 |
