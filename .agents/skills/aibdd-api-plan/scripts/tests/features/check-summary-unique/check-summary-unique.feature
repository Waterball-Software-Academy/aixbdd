Feature: operation summary global uniqueness check

  Rule: duplicate summaries inside one file are rejected
    Example: two operations in the same file share one summary
      Given a contract file at "orders.api.yml" with content:
        """
        openapi: 3.0.3
        info: {title: Orders, version: 1.0.0}
        paths:
          /orders:
            post:
              summary: 建立訂單
              responses: {'201': {description: created}}
            get:
              summary: 建立訂單
              responses: {'200': {description: ok}}
        """
      When check_summary_unique is run
      Then CLI exit code is 1
      And JSON ok is false
      And a violation "SUMMARY_UNIQUE" with detail containing "orders.api.yml#POST /orders"
      And a violation "SUMMARY_UNIQUE" with detail containing "orders.api.yml#GET /orders"

  Rule: duplicate summaries across files are rejected globally
    Example: two files each carry an operation with the same summary
      Given a contract file at "orders.api.yml" with content:
        """
        openapi: 3.0.3
        info: {title: Orders, version: 1.0.0}
        paths:
          /orders:
            post:
              summary: "建立訂單 "
              responses: {'201': {description: created}}
        """
      And a contract file at "sub/checkout.api.yml" with content:
        """
        openapi: 3.0.3
        info: {title: Checkout, version: 1.0.0}
        paths:
          /checkout:
            post:
              summary: 建立訂單
              responses: {'201': {description: created}}
        """
      When check_summary_unique is run
      Then CLI exit code is 1
      And JSON ok is false
      And a violation "SUMMARY_UNIQUE" with detail containing "sub/checkout.api.yml#POST /checkout"

  Rule: all-distinct summaries pass
    Example: every operation carries a distinct summary
      Given a contract file at "orders.api.yml" with content:
        """
        openapi: 3.0.3
        info: {title: Orders, version: 1.0.0}
        paths:
          /orders:
            post:
              summary: 建立訂單
              responses: {'201': {description: created}}
            get:
              summary: 查詢訂單列表
              responses: {'200': {description: ok}}
        """
      When check_summary_unique is run
      Then CLI exit code is 0
      And JSON ok is true
      And violations are empty

  Rule: an operation without summary is a violation
    Example: one operation misses the summary field
      Given a contract file at "orders.api.yml" with content:
        """
        openapi: 3.0.3
        info: {title: Orders, version: 1.0.0}
        paths:
          /orders:
            post:
              responses: {'201': {description: created}}
        """
      When check_summary_unique is run
      Then CLI exit code is 1
      And JSON ok is false
      And a violation "SUMMARY_MISSING" with detail containing "orders.api.yml#POST /orders"
