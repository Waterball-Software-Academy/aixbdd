1. `BVA` 只 EMIT point name，不 EMIT concrete value。
2. 先 CHECK `predicate_shape` 是否具有可測 boundary；沒有 boundary 就不 EMIT `bva_points`。
3. 合法 point name 只有：
   1. `min-minus-1`：值剛落在最小合法邊界之外。
   2. `min`：值剛好等於最小合法邊界。
   3. `nominal`：值落在合法區間內，且不是邊界值。
   4. `max`：值剛好等於最大合法邊界。
   5. `max-plus-1`：值剛落在最大合法邊界之外。
4. 單邊 predicate 只保留有語意的一側；另一側為 N/A，不得硬補。
5. 只保留符合 `test_direction` 的 points：
   1. `success`：保留位於合法域內或貼近合法邊界的 points。
   2. `failure`：保留位於非法域內或剛跨出邊界的 points。
6. 若 boundary 無法決定，或 point 與 `test_direction` 的對應無法判定，EMIT CiC，不做猜測。
