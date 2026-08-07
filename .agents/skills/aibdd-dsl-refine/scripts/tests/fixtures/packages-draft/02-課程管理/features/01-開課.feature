# 推導中：定義只落在 .dsl.yml.draft（尚未經 batch review 核可），worklist 必須仍算 pending。
Feature: 開課

  Rule: 後置（狀態） - 開課後課程落庫

    Example: 教練開一堂課程，開課成功
      Given 現在時間為 "2026-03-01T10:00:00+08:00"
      When "王教練" 開一堂 "有氧課" 課程
