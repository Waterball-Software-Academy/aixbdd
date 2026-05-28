1. `EP` 只 EMIT class name，不 EMIT concrete value。
2. 先 CLASSIFY `predicate_shape`，再從該 shape 的固定 class set 內挑選；不得自造名稱。
3. 支援的 shape 與 class set：
   1. `numeric-range`
      1. `below-range`：值落在合法區間下方。
      2. `at-lower-boundary`：值剛好等於下界。
      3. `within-range`：值落在合法區間內，且不是邊界值。
      4. `at-upper-boundary`：值剛好等於上界。
      5. `above-range`：值落在合法區間上方。
   2. `format-regex`
      1. `matching-pattern`：值符合指定格式。
      2. `mismatching-pattern`：值不符合指定格式，但仍是非空內容。
      3. `empty`：值為空字串。
      4. `whitespace-only`：值只包含空白字元。
   3. `enum`
      1. 每個 allowed enum value 各一 class：該 class 代表值恰為對應的合法常數。
      2. `outside-enum`：值不屬於任何 allowed enum value。
   4. `existence`
      1. `exists`：目標存在。
      2. `not-exists`：目標不存在。
   5. `boolean`
      1. `true-case`：值為 `true`。
      2. `false-case`：值為 `false`。
   6. `length`
      1. `too-short`：長度低於最小限制。
      2. `at-min-length`：長度剛好等於最小限制。
      3. `nominal-length`：長度位於合法區間內，且不是邊界值。
      4. `at-max-length`：長度剛好等於最大限制。
      5. `too-long`：長度超過最大限制。
4. 只保留符合 `test_direction` 的 classes：
   1. `success`：保留滿足 predicate 的 classes。
   2. `failure`：保留違反 predicate 的 classes。
5. 若 `predicate_shape` 無法決定，或無法判定哪個 class 屬於 success / failure side，EMIT CiC，不做猜測。
