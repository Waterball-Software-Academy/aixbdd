Feature: shared fixture step writes doc string content to per-scenario tempdir

  Background:
    Given a temporary file at "hello.txt" with content:
      """
      hello world
      """

  Rule: 後置（狀態）- context.last_file_path 應指向已寫入內容的暫存檔
    Example: 單檔寫入後從 last_file_path 讀回原文
      When the file at context.last_file_path is read
      Then the read content is "hello world"

  Rule: 後置（狀態）- alias 變體應將檔案路徑收進 context.files[alias]
    Example: alias 變體寫入第二檔後從 context.files["B"] 讀回原文
      Given a temporary file at "second.txt" with content (saved as "B"):
        """
        second file
        """
      When the file at context.files["B"] is read
      Then the read content is "second file"
