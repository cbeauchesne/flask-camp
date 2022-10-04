You can use JSON schema to validate your data. Simply declare what are the schemas using this code : 

```python
app = Application()

app.register_schemas("/dir/with/your/schemas/", ["schema_1.json", "schema_2.json"])
```

## Reference to other schemas

You can use json schema references inside your schema if they are present in your schema dir:

*/dir/with/your/schemas/schema_1.json:*

```json
{
  "properties": {
    "value": { "type": "string" },
    "rating": { "$ref": "entities/rating.json" }
  }
}
```

*/dir/with/your/schemas/entities/rating.json:*
```json
{
  "enum": ["6a", "6b"]
}
```

## Conditionnal schemas

One common need is to define schema only for a given namespace. A good design to achieve this is to declare as many schema as you have namespace: 

```json
{
  "if": {
    "properties": { "namespace": { "const": "outing" } }
  },
  "then": {
    "properties": {
      "data": {
        "properties": {
          "specific_outing_property": { "type": "string" },
        }
      }
    }
  }
}
```
