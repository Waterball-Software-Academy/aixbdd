Feature: OpenAPISpecParser flattens allOf-composed schemas into request/response fields

  Rule: 後置（狀態）- response schema 的 inline allOf 兩片段 properties 全收齊
    Example: createReport 的 200 response 由 allOf 組合 createdBy + status
      Given a temporary file at "contracts/reports.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Reports API
          version: 1.0.0
        paths:
          /reports:
            post:
              operationId: createReport
              responses:
                '200':
                  description: OK
                  content:
                    application/json:
                      schema:
                        allOf:
                          - type: object
                            properties:
                              createdBy:
                                type: string
                          - type: object
                            properties:
                              status:
                                type: string
        """
      When OpenAPISpecParser parses the last file
      Then the part's response_properties has entries:
        | name      | json_path    |
        | createdBy | $.createdBy  |
        | status    | $.status     |
      And the response_property named "createdBy" has target_part_path "contracts/reports.api.yml#/paths/~1reports/post/responses/200/content/application~1json/schema/allOf/0/properties/createdBy"
      And the response_property named "status" has target_part_path "contracts/reports.api.yml#/paths/~1reports/post/responses/200/content/application~1json/schema/allOf/1/properties/status"

  Rule: 後置（狀態）- requestBody 的 inline allOf 收齊 properties 且 required 取片段聯集
    Example: createReport 的 body 由 allOf 組合，title 必填、note 選填
      Given a temporary file at "contracts/reports.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Reports API
          version: 1.0.0
        paths:
          /reports:
            post:
              operationId: createReport
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      allOf:
                        - type: object
                          required: [title]
                          properties:
                            title:
                              type: string
                        - type: object
                          properties:
                            note:
                              type: string
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name  | source | required |
        | title | body   | true     |
        | note  | body   | false    |

  Rule: 後置（狀態）- allOf 片段為跨檔 $ref 時，properties 合併且各自落 definition-site
    Example: response 由 common.yml 的 Audit 與 inline status 組合
      Given a temporary file at "contracts/common.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Common
          version: 1.0.0
        components:
          schemas:
            Audit:
              type: object
              properties:
                createdBy:
                  type: string
        """
      And a temporary file at "contracts/reports.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Reports API
          version: 1.0.0
        paths:
          /reports:
            post:
              operationId: createReport
              responses:
                '200':
                  description: OK
                  content:
                    application/json:
                      schema:
                        allOf:
                          - $ref: 'common.yml#/components/schemas/Audit'
                          - type: object
                            properties:
                              status:
                                type: string
        """
      When OpenAPISpecParser parses the last file
      Then the part's response_properties has entries:
        | name      | json_path   |
        | createdBy | $.createdBy |
        | status    | $.status    |
      And the response_property named "createdBy" has target_part_path "contracts/common.yml#/components/schemas/Audit/properties/createdBy"
      And the response_property named "status" has target_part_path "contracts/reports.api.yml#/paths/~1reports/post/responses/200/content/application~1json/schema/allOf/1/properties/status"

  Rule: 後置（狀態）- schema 以 $ref 指向內部使用 allOf 的 component，properties 仍攤平
    Example: response 指向 ReportView（內部 allOf），id 與 status 皆收齊
      Given a temporary file at "contracts/reports.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Reports API
          version: 1.0.0
        components:
          schemas:
            ReportView:
              allOf:
                - type: object
                  properties:
                    id:
                      type: string
                - type: object
                  properties:
                    status:
                      type: string
        paths:
          /reports:
            post:
              operationId: createReport
              responses:
                '200':
                  description: OK
                  content:
                    application/json:
                      schema:
                        $ref: '#/components/schemas/ReportView'
        """
      When OpenAPISpecParser parses the last file
      Then the part's response_properties has entries:
        | name   | json_path  |
        | id     | $.id       |
        | status | $.status   |
      And the response_property named "id" has target_part_path "contracts/reports.api.yml#/components/schemas/ReportView/allOf/0/properties/id"
      And the response_property named "status" has target_part_path "contracts/reports.api.yml#/components/schemas/ReportView/allOf/1/properties/status"
