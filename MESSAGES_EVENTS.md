# Messages and events


This microservice listens to the following events:

| Event description     | Routing Key       | Procedure invoked               | Parameters  |
|:----------------------|:------------------|:--------------------------------|:------------|
|A customer is deleted  |CUSTOMER_DELETION  |delete_all_user_reservation      |customer_id  |
|A restaurant is deleted|RESTAURANT_DELETION|delete_all_restaurant_reservation|restaurant_id|


## RPC <small>Remote Procedure Call<small>

This microservice offers this operations:

|Operation name                         | Procedure invoked                     | Parameters  | Return type |
|---------------------------------------|---------------------------------------|-------------|-------------|
|retrieve_by_customer_id                |retrieve_by_customer_id                |customer_id  |JSON         |
|retrieve_all_contact_reservation_by_id |retrieve_all_contact_reservation_by_id |customer_id  |JSON         |
|retrieve_by_customer_id_in_future      |retrieve_by_customer_id_in_future      |customer_id  |JSON         |
|retrieve_by_customer_id_in_last_14_days|retrieve_by_customer_id_in_last_14_days|customer_id  |JSON         |

### Message composition

The request for RCP should be formatted as JSON standard and must contains func keyword and operation parameters.
For example:

```json
{
"func": "retrieve_by_customer_id",
"customer_id": "3"
}
```