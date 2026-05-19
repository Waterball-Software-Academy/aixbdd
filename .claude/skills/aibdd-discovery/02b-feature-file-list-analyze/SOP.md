
# SOP

1. THINK: 拆解 `${PLAN_SPEC}` 中需求敘述的每一段話，進行段落流程建模分析。 標註每一段話為 $P，所有話的集合為 all $P
2. FAITHFUL REASONING: FOR EACH $P，萃取此段落句子中的 RESTFul API，請勿捕捉句子中不存在的元素，因此捕捉過程針對每一個捕捉物都要明確指出他對應的證據。
    - $FeatureFiles = 嚴格遵照 `rules/apiwise-granularity.md` 的顆粒度定義來萃取。
    - $GAPS = 當你發現底下現象時，將此現象記錄起來儲存於內部推理思考的 GAPS 空間中：
        - 針對某個 Feature File 不確定他的顆粒度是否正確，是否應該被列為 Feature File