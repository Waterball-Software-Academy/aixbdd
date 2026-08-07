# 事故蒸餾：SKILL-GAPS #52——params 預設值不經衍生區的字面正規化，
# 「feature 供值」與「param 預設」走兩套格式，直到 green 才炸。
Feature: 課程開課

  Rule: 後置（狀態） - 開課後課程落庫

    Example: 教練開一堂課程，開課成功
      Given 現在時間為 "2026-03-01T10:00:00+08:00"
      When "王教練" 開一堂 "有氧課" 課程
      Then 系統回應 "開課成功"
