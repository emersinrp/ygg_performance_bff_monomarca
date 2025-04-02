def get_delivery_window_query():
    return {
        "query": """
        query ValidacaoDeliveryWindow($buyer_codes: [String!]!, $allowed_low_shelf_life: Boolean) {
          get_person_delivery_window(
            filters: {buyer_codes: $buyer_codes, allowed_low_shelf_life: $allowed_low_shelf_life, only_valids_delivery_windows: true}
          ) {
            items {
              delivery_windows {
                allowed_low_shelf_life
                delivery_date
              }
            }
          }
        }
        """,
        "variables": {
            "buyer_codes": ["0000247276"],
            "allowed_low_shelf_life": True
        }
    }