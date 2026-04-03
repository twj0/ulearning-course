# DGUT Ulearning 测试页记录数据模型说明

## 1. 文档目的

本文档面向当前项目自己的 Python 代码，目标不是复述前端实现，而是回答两个问题：

1. 我们应该如何在自己的代码里表达 UA 测试页学习记录结构。
2. 在不依赖浏览器前端组件的前提下，我们最多能做哪些“题目交互”。

这里的“题目交互”仅指：

- 读取题目结构
- 读取标准答案
- 读取历史学习记录
- 用数据模型表达题目作答状态

不包含伪装点击、绕过页面流程或模拟浏览器交互。

## 2. 当前项目模型的缺口

当前 [study_record.py](D:/py_work/2026/ulearning-course/src/ulearning_course/models/study_record.py) 只覆盖了：

- `StudyRecord`
- `PageRecord`
- `VideoRecord`

也就是当前模型更偏“视频页学习记录”，还没有把测试页真正需要的字段表达出来。

### 2.1 目前缺失的测试页字段

| 层级 | 当前是否覆盖 | 缺失字段 |
| --- | --- | --- |
| 小节层 `StudyRecord` | 部分覆盖 | `completion_status` / `item_id` 兼容解析、`learner_name`、`activity_title`、`version` |
| 页面层 `PageRecord` | 部分覆盖 | `answer_time`、`submit_times`、`coursepage_id`、`questions`、`speaks` |
| 题目层 | 未覆盖 | `questionid`、`answerList`、`score` |

## 3. 建议的数据模型分层

对 UA 学习记录，建议统一分成四层：

1. `StudyRecord`
2. `PageRecord`
3. `QuestionRecord`
4. `VideoRecord`

其中测试页最关键的是页面层和题目层。

### 3.1 小节层

建议字段：

| Python 字段 | UA 原字段 | 含义 |
| --- | --- | --- |
| `item_id` | `itemid` 或 `item_id` | 小节 ID |
| `complete` | `complete` 或 `completion_status` | 小节完成状态 |
| `score` | `score` | 小节总分 |
| `study_start_time` | `studyStartTime` | 当前学习会话时间戳 |
| `learner_name` | `learner_name` | 学习记录返回中的用户名 |
| `activity_title` | `activity_title` | 小节标题 |
| `pages` | `pageStudyRecordDTOList` | 页面记录列表 |

### 3.2 页面层

建议字段：

| Python 字段 | UA 原字段 | 含义 |
| --- | --- | --- |
| `page_id` | `pageid` | 页面记录 ID |
| `complete` | `complete` | 页面完成状态 |
| `study_time` | `studyTime` | 页面学习时长 |
| `score` | `score` | 页面得分 |
| `answer_time` | `answerTime` | 页面答题时间相关字段 |
| `submit_times` | `submitTimes` | 页面提交次数 |
| `coursepage_id` | `coursepageId` | 练习组件 ID |
| `questions` | `questions` | 题目记录列表 |
| `videos` | `videos` | 视频记录列表 |
| `speaks` | `speaks` | 口语记录列表 |

### 3.3 题目层

建议新增 `QuestionRecord`：

| Python 字段 | UA 原字段 | 含义 |
| --- | --- | --- |
| `question_id` | `questionid` | 单题 ID |
| `answer_list` | `answerList` | 用户答案数组 |
| `score` | `score` | 单题得分 |

### 3.4 视频层

现有 `VideoRecord` 基本够用：

| Python 字段 | UA 原字段 |
| --- | --- |
| `video_id` | `videoid` |
| `current` | `current` |
| `status` | `status` |
| `record_time` | `recordTime` |
| `time` | `time` |
| `start_end_time_list` | `startEndTimeList` |

## 4. 推荐的 Python 表达方式

如果后面要把模型落进代码，最稳妥的是下面这种结构：

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QuestionRecord:
    question_id: int
    answer_list: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class VideoRecord:
    video_id: int
    current: float
    status: int
    record_time: float
    time: float
    start_end_time_list: list = field(default_factory=list)


@dataclass
class PageRecord:
    page_id: int
    complete: int
    study_time: int
    score: int
    answer_time: int = 0
    submit_times: int = 0
    coursepage_id: Optional[int] = None
    questions: list[QuestionRecord] = field(default_factory=list)
    videos: list[VideoRecord] = field(default_factory=list)
    speaks: list = field(default_factory=list)


@dataclass
class StudyRecord:
    item_id: int
    complete: int
    score: int
    study_start_time: Optional[int] = None
    learner_name: Optional[str] = None
    activity_title: Optional[str] = None
    pages: list[PageRecord] = field(default_factory=list)
```

## 5. 解析策略建议

由于 UA 的读取接口和同步包字段并不完全一致，建议解析时做“兼容映射”，不要写死成只认一套字段名。

### 5.1 小节层兼容规则

| 读取来源 | 建议取值 |
| --- | --- |
| `itemid` 存在 | 优先用 `itemid` |
| `item_id` 存在 | 回退用 `item_id` |
| `complete` 存在 | 优先用 `complete` |
| `completion_status` 存在 | 回退用 `completion_status` |

### 5.2 页面层兼容规则

| 字段 | 建议 |
| --- | --- |
| `questions` 不存在 | 默认空列表 |
| `videos` 不存在 | 默认空列表 |
| `speaks` 不存在 | 默认空列表 |
| `submitTimes` 不存在 | 默认 `0` |
| `coursepageId` 不存在 | 默认 `None` |

## 6. 这套模型能支持什么

如果只做“数据表达”和“记录读取”，这套模型已经足够支持：

1. 判断一个小节是视频页还是测试页。
2. 读取测试页已保存的 `submit_times`。
3. 读取测试页每道题历史答案。
4. 读取测试页页面总分和小节总分。
5. 区分“页面已完成”和“题目得分是否大于 0”。

## 7. 不用前端，能不能进行题目交互

可以分成“能做”和“不能直接证明能做”的两部分。

### 7.1 可以做的部分

在当前证据下，不依赖浏览器前端，也能做这些事情：

| 能力 | 是否可行 | 依据 |
| --- | --- | --- |
| 读取题目结构 | 可以 | `wholepage/chapter/stu/<chapterNodeId>` 返回 `questionDTOList` |
| 读取标准答案 | 可以 | `GET /uaapi/questionAnswer/<questionid>?parentId=<pageId>` |
| 读取历史作答记录 | 可以 | `GET /uaapi/studyrecord/item/<itemid>?courseType=4` |
| 用本地代码表达题目答案与得分 | 可以 | `questions[]` 结构已明确 |

### 7.2 不能简单等同为“完整交互”的部分

下面这些事情，当前不能仅因为“接口看懂了”就视为已经稳定可做：

| 能力 | 当前结论 |
| --- | --- |
| 不靠前端就完整复现页面答题状态机 | 不能直接证明 |
| 不靠前端就稳定复现提交时机 | 不能直接证明 |
| 不靠前端就完整复现 `submitTimes`、`complete`、自动保存节奏 | 不能直接证明 |
| 不靠前端就证明服务端完全不校验上下文 | 不能直接证明 |

### 7.3 边界结论

更准确的说法是：

- 不用前端，也可以“读取题目”和“读取答案”。
- 不用前端，也可以“读取已经落库的题目作答记录”。
- 但“不用前端就能完整替代测试页交互流程”目前没有充分证据。

所以，在我们自己的代码里，合理目标应该是：

1. 先把测试页记录结构建模完整。
2. 把“读题”“读答案”“读历史记录”三件事做成稳定的数据层能力。
3. 不把当前项目的数据模型设计成依赖浏览器组件。

## 8. 对当前项目的具体建议

结合现有代码，最适合的方向是：

| 模块 | 建议 |
| --- | --- |
| `models/study_record.py` | 增加 `QuestionRecord`，扩展 `PageRecord` 字段 |
| `StudyRecord.from_dict()` | 改成兼容测试页/视频页两类数据 |
| `StudyClient.get_study_record()` | 保持只读接口即可，不耦合“是否必须能提交” |
| `docs/network/` | 保留“测试页记录结构”和“交互边界”文档说明 |

## 9. 参考文档

| 文档 | 说明 |
| --- | --- |
| `03-api-study-record-and-sync.md` | 学习记录与同步主链路 |
| `06-api-request-and-response-examples.md` | 真实请求与响应样例 |
| `12-api-test-page-and-question-answer.md` | 测试页答案接口与提交链路 |
