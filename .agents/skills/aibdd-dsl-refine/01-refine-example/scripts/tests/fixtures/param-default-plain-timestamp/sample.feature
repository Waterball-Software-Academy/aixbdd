# 對照組：專案的 ISA 值域本來就吃 `yyyy-MM-dd HH:mm:ss`，feature 沒有任何 ISO-8601 供值，
# 這種 param 預設不是 #52 的格式漂移——只提醒、不阻斷（驗收期以 golden after/ 實測發現）。
Feature: 課程開課

  Rule: 後置（狀態） - 開課後課程落庫

    Example: 教練開一堂課程，開課成功
      Given 系統中已有一位 "王教練"
      When "王教練" 開一堂 "有氧課" 課程
      Then 系統回應 "開課成功"
