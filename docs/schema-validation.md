You can use JSON schema to validate your data. Simply declare what are the schemas using this code : 

```python
api = RestApi(schemas_directory="/directory/with/your/schemas/", document_schemas=["schema_1.json", "schema_2.json"])
```

Files `/directory/with/your/schemas/schema_1.json` and `/directory/with/your/schemas/schema_2.json` must exists

## Reference to other schemas

You can use json schema references inside your schema if they are present in your schema dir:

*/directory/with/your/schemas/schema_1.json:*

```json
{
  "properties": {
    "value": { "type": "string" },
    "rating": { "$ref": "entities/rating.json" }
  }
}
```

*/directory/with/your/schemas/entities/rating.json:*
```json
{
  "enum": ["6a", "6b"]
}
```
