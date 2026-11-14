# 需求状态与门槛

流程状态与代码是否存在、是否封存、是否部署是不同事实。状态只在需求池维护。

| 状态 | 进入依据 |
| --- | --- |
| candidate | 有真实来源与问题登记 |
| collecting | 明确缺少资料并开始收集 |
| analyzing | 分析用户价值、依赖、成本与可行性 |
| defined | 负责人确认问题、范围与验收定义 |
| reviewing | 有可评审PRD、待决问题与相关参与人 |
| approved | 负责人明确批准，并保留证据 |
| developing | 已批准范围进入实施，开发入口明确 |
| validating | 实现进入真实执行验证，保留结果 |
| released | 有对应交付或真实运行验证，并经发布确认 |
| closed | 负责人确认本轮目标处置完成、复盘与遗留已记录 |

完整链为candidate → collecting → analyzing → defined → reviewing → approved → developing → validating → released → closed。无需机械地为了状态补造会议，但任何跳转都要有真实依据和负责人确认。AI不能给自己签字。

approved以后出现实质范围变化，记录原因并回到reviewing。目标版本在需求池只是计划，承诺以版本scope为准。优先级用P0/P1/P2/P3并说明依据；无法判断写未评定，不冒充业务决策。

构建成功、代码合入、平台返回任务ID都不是released。没有真实环境时可以完成某些本地验收，但要保留未覆盖范围，不能把模拟验证改名为上线验证。需求取消、延期或被替代时先记录实际决定，不强制把未完成工作伪装为released再closed。
