# MCP/OpenAI 格式的工具定义，供 LLM function calling 使用

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_product",
            "description": "添加一个新商品到数据库（单条）",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "商品名称"},
                    "price": {"type": "number", "description": "商品价格"},
                    "stock": {"type": "integer", "description": "库存数量"}
                },
                "required": ["name", "price", "stock"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_products",
            "description": "一次添加多个商品。用户说“依次添加A、B、C”或“批量添加”时使用此工具，传入商品列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "description": "商品列表，每项包含 name、price、stock",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "商品名称"},
                                "price": {"type": "number", "description": "商品价格"},
                                "stock": {"type": "integer", "description": "库存数量"}
                            },
                            "required": ["name", "price", "stock"]
                        }
                    }
                },
                "required": ["products"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_product_by_name",
            "description": "根据商品名称删除商品。用户说「删除草莓」「去掉苹果商品」「移除名为梨的商品」等时，必须用此工具而不是 query_products。传入商品名称或名称关键词即可，会删除名称匹配的所有记录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "要删除的商品名称或名称关键词"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_product",
            "description": "根据商品ID删除一个商品。仅在用户明确给出ID时使用；若用户只说商品名称（如删除草莓），请用 delete_product_by_name。",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "要删除的商品ID"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_products",
            "description": "批量根据ID删除多个商品，传入ID列表。仅当用户明确给出多个具体ID时使用。若用户说「删除前/后三个」「按顺序去掉前几条」等，用 delete_first_n_products 或 delete_last_n_products。",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "description": "要删除的商品ID列表",
                        "items": {"type": "integer"}
                    }
                },
                "required": ["product_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_first_n_products",
            "description": "按入库顺序删除前 n 个商品。用户说「删除前三个」「去掉前两条」等用此工具，传入 n。",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "要删除的前 n 个（按入库顺序）"}
                },
                "required": ["n"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_last_n_products",
            "description": "按入库顺序删除后 n 个商品。用户说「删除后三个」「去掉最后两条」等用此工具，传入 n。",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "要删除的后 n 个（按入库顺序）"}
                },
                "required": ["n"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_product",
            "description": "更新一个商品的信息（至少提供一个要更新的字段）",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "要更新的商品ID"},
                    "name": {"type": "string", "description": "新的商品名称（可选）"},
                    "price": {"type": "number", "description": "新的价格（可选）"},
                    "stock": {"type": "integer", "description": "新的库存（可选）"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_products",
            "description": "仅用于「查看、查询、列出、显示、有多少、几个」等只读意图。数据格式只有名称、价格、库存；前/后几条按入库顺序。库存大于100→stock_min=101；价格2到8元→price_min=2,price_max=8。按名称用 condition。问数量时设 return_count_only=true。",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "商品名称关键词，模糊匹配（可选）"},
                    "price_min": {"type": "number", "description": "最低价格（可选）"},
                    "price_max": {"type": "number", "description": "最高价格（可选）"},
                    "stock_min": {"type": "integer", "description": "最低库存（可选）。库存大于N→stock_min=N+1。"},
                    "stock_max": {"type": "integer", "description": "最高库存（可选）"},
                    "return_count_only": {"type": "boolean", "description": "是否只返回数量不列明细。"},
                    "limit": {"type": "integer", "description": "前几条（按入库顺序）。用户说「前三个」「列出前5条」时填 3、5。"},
                    "last_n": {"type": "integer", "description": "后几条（按入库顺序）。用户说「后三个」「最后5条」时填 3、5。"}
                },
                "required": []
            }
        }
    }
]
